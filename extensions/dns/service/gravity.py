# extensions/dns/service/gravity.py
from __future__ import annotations

import asyncio
import pathlib
import time
from typing import Iterable, Dict, Set, List

import aiohttp
import yaml


class GravityUpdater:
    """
    Periodically fetches blocklists and threat feeds, writes:
      - blocklist.txt
      - categories.yaml (domains + inheritance)
    and exposes lightweight analytics for the API:
      - last_update_ts
      - rule_count
      - threat_rule_count
      - sources
    """

    def __init__(self, rules_path: pathlib.Path, config: dict):
        # If config doesn't specify, default to the standard rules dir
        if not str(rules_path):
            rules_path = pathlib.Path("extensions/dns/rules")

        self.rules_path = rules_path
        self.config = config

        self.blocklist_file = self.rules_path / "blocklist.txt"
        self.sources_file = self.rules_path / "sources.yaml"
        self.threat_feeds_file = self.rules_path / "threat_feeds.yaml"
        self.categories_file = self.rules_path / "categories.yaml"

        # Analytics fields used by /api/dns/gravity
        self.last_update_ts: float | None = None
        self.rule_count: int = 0
        self.threat_rule_count: int = 0
        self.sources: List[dict] = []

        # Ensure rules directory exists
        self.rules_path.mkdir(parents=True, exist_ok=True)

    async def run_periodic(self):
        interval_hours = float(
            self.config.get("gravity", {}).get("interval_hours", 12)
        )
        while True:
            try:
                await self.update_once()
            except Exception as e:
                print("[DNS][gravity] update failed:", e)
            await asyncio.sleep(interval_hours * 3600)

    async def update_once(self):
        domains: Set[str] = set()
        domain_categories: Dict[str, Set[str]] = {}

        total_from_sources = 0
        total_from_threats = 0
        collected_sources: List[dict] = []

        # --------------------------------------------------------
        # HOSTS-STYLE SOURCES
        # --------------------------------------------------------
        if self.sources_file.exists():
            cfg = yaml.safe_load(self.sources_file.read_text()) or {}
            sources = cfg.get("sources", [])
            async with aiohttp.ClientSession() as session:
                for src in sources:
                    url = src.get("url")
                    name = src.get("name", url)
                    if not url:
                        continue
                    cats = set(src.get("categories", []))
                    if not cats:
                        cats = {"ads"}

                    collected_sources.append({"name": name, "url": url})

                    print(f"[DNS][gravity] fetching {name} ({url})")
                    try:
                        async with session.get(url, timeout=60) as resp:
                            text = await resp.text()
                            count_before = len(domains)
                            for d in self._extract_domains(text.splitlines()):
                                domains.add(d)
                                domain_categories.setdefault(d, set()).update(cats)
                            added = len(domains) - count_before
                            total_from_sources += added
                            print(
                                f"[DNS][gravity] {name}: added {added} domains "
                                f"(total {len(domains)})"
                            )
                    except Exception as e:
                        print(f"[DNS][gravity] failed {name} ({url}): {e}")

        # --------------------------------------------------------
        # THREAT FEEDS
        # --------------------------------------------------------
        if self.threat_feeds_file.exists():
            cfg = yaml.safe_load(self.threat_feeds_file.read_text()) or {}
            feeds = cfg.get("feeds", [])
            async with aiohttp.ClientSession() as session:
                for feed in feeds:
                    url = feed.get("url")
                    name = feed.get("name", url)
                    cat = feed.get("category")
                    if not url or not cat:
                        continue

                    collected_sources.append({"name": name, "url": url, "category": cat})

                    print(f"[DNS][gravity] fetching threat feed {name} ({url})")
                    try:
                        async with session.get(url, timeout=60) as resp:
                            text = await resp.text()
                            count_before = len(domains)
                            for d in self._extract_domains(text.splitlines()):
                                domains.add(d)
                                domain_categories.setdefault(d, set()).add(cat)
                            added = len(domains) - count_before
                            total_from_threats += added
                            print(
                                f"[DNS][gravity] threat feed {name}: added {added} domains "
                                f"(total {len(domains)})"
                            )
                    except Exception as e:
                        print(f"[DNS][gravity] threat feed failed {name} ({url}): {e}")

        # --------------------------------------------------------
        # WRITE BLOCKLIST
        # --------------------------------------------------------
        if domains:
            self.blocklist_file.write_text("\n".join(sorted(domains)))
            print(
                f"[DNS][gravity] wrote {len(domains)} domains to {self.blocklist_file}"
            )
        else:
            print("[DNS][gravity] no domains collected; blocklist.txt not updated")

        # --------------------------------------------------------
        # MERGE CATEGORIES INTO categories.yaml
        # --------------------------------------------------------
        self._update_categories_file(domain_categories)

        # --------------------------------------------------------
        # UPDATE ANALYTICS FIELDS
        # --------------------------------------------------------
        self.last_update_ts = time.time()
        self.rule_count = len(domains)
        self.threat_rule_count = total_from_threats
        self.sources = collected_sources

        print(
            "[DNS][gravity] update complete: "
            f"{self.rule_count} total domains, "
            f"{self.threat_rule_count} from threat feeds, "
            f"{len(self.sources)} sources"
        )

    def _extract_domains(self, lines: Iterable[str]) -> Iterable[str]:
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            # hosts-style: "0.0.0.0 domain.com"
            if len(parts) == 1:
                yield parts[0].lower()
            elif len(parts) >= 2:
                yield parts[1].lower()

    def _update_categories_file(self, domain_categories: Dict[str, Set[str]]):
        existing_domains: Dict[str, Set[str]] = {}
        inheritance: Dict[str, Set[str]] = {}

        if self.categories_file.exists():
            try:
                data = yaml.safe_load(self.categories_file.read_text()) or {}
                for d, cats in (data.get("domains", {}) or {}).items():
                    existing_domains[d.lower()] = set(cats or [])
                for cat, children in (data.get("inheritance", {}) or {}).items():
                    inheritance[cat] = set(children or [])
            except Exception as e:
                print("[DNS][gravity] failed to read categories.yaml:", e)

        # Default inheritance if none present
        if not inheritance:
            inheritance = {
                "ads": {"tracking"},
                "tracking": set(),
                "malware": {"dangerous"},
                "phishing": {"dangerous"},
                "botnet": {"dangerous"},
                "c2": {"dangerous"},
                "cryptomining": {"resource_abuse"},
                "adult": {"nsfw"},
                "social": set(),
                "gambling": set(),
                "dangerous": set(),
                "resource_abuse": set(),
                "nsfw": set(),
            }

        for d, cats in domain_categories.items():
            existing_domains.setdefault(d, set()).update(cats)

        out = {
            "domains": {
                d: sorted(list(cats)) for d, cats in existing_domains.items()
            },
            "inheritance": {
                c: sorted(list(children)) for c, children in inheritance.items()
            },
        }
        self.categories_file.write_text(yaml.safe_dump(out))
        print(
            f"[DNS][gravity] updated categories.yaml with {len(existing_domains)} domains"
        )

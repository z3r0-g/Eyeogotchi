# extensions/dns/service/categories.py
from __future__ import annotations

from typing import Dict, Set
import pathlib
import os
import yaml


class CategoryResolver:
    """
    Resolves categories for a given qname based on categories.yaml.

    Auto-reloads categories.yaml when it changes on disk so that
    Gravity updates are reflected without restarting the plugin.
    """

    def __init__(self, config: dict):
        rules_path = pathlib.Path(config.get("rules_path", "extensions/dns/rules"))
        self.categories_file = rules_path / "categories.yaml"
        self.domains: Dict[str, Set[str]] = {}
        self.inheritance: Dict[str, Set[str]] = {}
        self._last_mtime: float = 0.0
        self._load()

    def _load(self):
        if not self.categories_file.exists():
            print("[DNS][categories] No categories.yaml found")
            self.domains = {}
            self.inheritance = {}
            self._last_mtime = 0.0
            return

        try:
            data = yaml.safe_load(self.categories_file.read_text()) or {}
            domains = data.get("domains", {})
            inheritance = data.get("inheritance", {})

            self.domains = {
                d.lower(): set(cats or []) for d, cats in domains.items()
            }
            self.inheritance = {
                cat: set(children or []) for cat, children in inheritance.items()
            }
            self._last_mtime = self.categories_file.stat().st_mtime

            print(
                f"[DNS][categories] Loaded {len(self.domains)} domains, "
                f"{len(self.inheritance)} inheritance rules"
            )
        except Exception as e:
            print("[DNS][categories] Failed to load categories.yaml:", e)
            self.domains = {}
            self.inheritance = {}
            self._last_mtime = 0.0

    def _maybe_reload(self):
        if not self.categories_file.exists():
            if self.domains or self.inheritance:
                # File disappeared; reset
                print("[DNS][categories] categories.yaml missing; clearing cache")
                self.domains = {}
                self.inheritance = {}
                self._last_mtime = 0.0
            return

        try:
            mtime = self.categories_file.stat().st_mtime
        except OSError:
            return

        if mtime > self._last_mtime:
            print("[DNS][categories] Detected categories.yaml change; reloading")
            self._load()

    def get_categories(self, qname: str) -> Set[str]:
        # Check if categories.yaml changed since last load
        self._maybe_reload()

        qname = qname.rstrip(".").lower()
        labels = qname.split(".")
        for i in range(len(labels)):
            candidate = ".".join(labels[i:])
            if candidate in self.domains:
                base = set(self.domains[candidate])
                return self._expand_inheritance(base)
        return set()

    def _expand_inheritance(self, cats: Set[str]) -> Set[str]:
        result = set(cats)
        stack = list(cats)
        while stack:
            c = stack.pop()
            children = self.inheritance.get(c, set())
            for child in children:
                if child not in result:
                    result.add(child)
                    stack.append(child)
        return result

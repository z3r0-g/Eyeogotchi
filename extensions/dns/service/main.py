# extensions/dns/service/main.py
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional
import pathlib

from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE

from core.system.extension_base import ExtensionBase
from core.event_bus.event_bus import EventBus  # type: ignore[unused-import]

from .gravity import GravityUpdater
from .ips import DNSIPS
from .telemetry import DNSTelemetry
from .policy import PolicyEngine
from .categories import CategoryResolver
from extensions.dns.api.events import record_dns_event


class DNSSinkholePlugin(ExtensionBase):
    """
    DNS sinkhole extension, adapted to the standard ExtensionBase(runtime) model.
    """

    name = "dns"

    def __init__(self, runtime):
        # Sets self.runtime, self.bus, self.config
        super().__init__(runtime)

        self.running = False

        self.server_task: Optional[asyncio.Task] = None
        self.gravity_task: Optional[asyncio.Task] = None

        self.blocklist = set()
        self.allowlist = set()
        self.rewrites: Dict[str, str] = {}

        self.categories = CategoryResolver(self.config)
        self.telemetry = DNSTelemetry()
        self.ips = DNSIPS(self.config)
        self.policy = PolicyEngine(self.config, self.categories)

        # NEW: Gravity object placeholder (API expects this)
        self.gravity: Optional[GravityUpdater] = None

    # ------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------
    def start(self) -> None:
        print("[DNS] Starting DNS Sinkhole plugin")
        self.running = True

        # DNS EVENT SUBSCRIPTIONS (Portal telemetry)
        self.bus.subscribe("dns.block", record_dns_event)
        self.bus.subscribe("dns.policy", record_dns_event)
        self.bus.subscribe("dns.rewrite", record_dns_event)
        self.bus.subscribe("dns.suspicious", record_dns_event)

        self._load_rules()

        loop = asyncio.get_event_loop()
        self.server_task = loop.create_task(self._run_dns_server())

        # --------------------------------------------------------
        # GRAVITY INITIALIZATION
        # --------------------------------------------------------
        if self.config.get("gravity", {}).get("enabled", True):
            rules_path = pathlib.Path(self.config.get("rules_path", ""))

            # Create GravityUpdater instance and expose it as self.gravity
            self.gravity = GravityUpdater(rules_path, self.config)

            # Start periodic updates
            self.gravity_task = loop.create_task(self.gravity.run_periodic())

            print("[DNS] Gravity updater started")
        else:
            print("[DNS] Gravity disabled in config")

        self.bus.publish("plugin.started", {"plugin": self.name})

    def stop(self) -> None:
        print("[DNS] Stopping DNS Sinkhole plugin")
        self.running = False

        if self.server_task:
            self.server_task.cancel()
        if self.gravity_task:
            self.gravity_task.cancel()

        self.bus.publish("plugin.stopped", {"plugin": self.name})

    def health(self) -> dict[str, Any]:
        base = {
            "status": "ok" if self.running else "stopped",
            "blocklist_size": len(self.blocklist),
            "allowlist_size": len(self.allowlist),
            "rewrite_rules": len(self.rewrites),
        }
        if self.config.get("telemetry", {}).get("enabled", True):
            base["telemetry"] = self.telemetry.snapshot()
        return base

    # ------------------------------------------------------------
    # RULE LOADING
    # ------------------------------------------------------------
    def _load_rules(self) -> None:
        rules_path = pathlib.Path(self.config.get("rules_path", ""))

        blocklist_file = rules_path / "blocklist.txt"
        allowlist_file = rules_path / "allowlist.txt"
        rewrites_file = rules_path / "rewrites.yaml"

        import yaml

        if blocklist_file.exists():
            self.blocklist = {
                line.strip().lower()
                for line in blocklist_file.read_text().splitlines()
                if line.strip()
            }

        if allowlist_file.exists():
            self.allowlist = {
                line.strip().lower()
                for line in allowlist_file.read_text().splitlines()
                if line.strip()
            }

        if rewrites_file.exists():
            self.rewrites = yaml.safe_load(rewrites_file.read_text()) or {}

        print(
            f"[DNS] Loaded rules: {len(self.blocklist)} blocked, "
            f"{len(self.allowlist)} allowed, {len(self.rewrites)} rewrites"
        )

    # ------------------------------------------------------------
    # DNS SERVER
    # ------------------------------------------------------------
    async def _run_dns_server(self):
        listen_host = self.config.get("listen_host", "0.0.0.0")
        listen_port = int(self.config.get("listen_port", 5353))

        print(f"[DNS] Listening on {listen_host}:{listen_port}")

        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DNSProtocol(self),
            local_addr=(listen_host, listen_port),
        )

        try:
            while self.running:
                await asyncio.sleep(0.1)
        finally:
            transport.close()

    async def handle_query(self, data: bytes, addr, transport):
        client_ip = addr[0]

        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).rstrip(".").lower()
            qtype = QTYPE[request.q.qtype]

            cats = self.categories.get_categories(qname)

            if self.config.get("telemetry", {}).get("enabled", True):
                self.telemetry.record_query(qname, client_ip, cats)

            self.bus.publish(
                "dns.query",
                {
                    "query": qname,
                    "type": qtype,
                    "client": client_ip,
                    "categories": list(cats),
                    "timestamp": time.time(),
                },
            )

            # Policy engine
            if self.config.get("policy", {}).get("enabled", True):
                decision = self.policy.evaluate(client_ip, qname)
                if decision:
                    if decision.action == "allow":
                        resp = await self._forward_to_upstream(request)
                        self.bus.publish(
                            "dns.policy",
                            {
                                "query": qname,
                                "client": client_ip,
                                "action": "allow",
                                "reason": decision.reason,
                            },
                        )
                        transport.sendto(resp.pack(), addr)
                        return

                    if decision.action == "block":
                        if self.config.get("telemetry", {}).get("enabled", True):
                            self.telemetry.record_block(cats)
                        resp = self._make_response(request, "0.0.0.0")
                        self.bus.publish(
                            "dns.policy",
                            {
                                "query": qname,
                                "client": client_ip,
                                "action": "block",
                                "reason": decision.reason,
                                "categories": list(cats),
                            },
                        )
                        transport.sendto(resp.pack(), addr)
                        return

                    if decision.action == "rewrite" and decision.rewrite_ip:
                        resp = self._make_response(request, decision.rewrite_ip)
                        self.bus.publish(
                            "dns.policy",
                            {
                                "query": qname,
                                "client": client_ip,
                                "action": "rewrite",
                                "reason": decision.reason,
                                "ip": decision.rewrite_ip,
                                "categories": list(cats),
                            },
                        )
                        transport.sendto(resp.pack(), addr)
                        return

            # IPS
            if self.config.get("ips", {}).get("enabled", True):
                ips_decision = self.ips.analyze(qname)
                if ips_decision and ips_decision.suspicious:
                    if self.config.get("telemetry", {}).get("enabled", True):
                        self.telemetry.record_suspicious()
                    self.bus.publish(
                        "dns.suspicious",
                        {
                            "query": qname,
                            "client": client_ip,
                            "reason": ips_decision.reason,
                            "categories": list(cats),
                            "timestamp": time.time(),
                        },
                    )

            # Allowlist
            if qname in self.allowlist:
                resp = await self._forward_to_upstream(request)
                transport.sendto(resp.pack(), addr)
                return

            # Rewrites
            if qname in self.rewrites:
                ip = self.rewrites[qname]
                resp = self._make_response(request, ip)
                self.bus.publish(
                    "dns.rewrite",
                    {
                        "query": qname,
                        "client": client_ip,
                        "ip": ip,
                        "categories": list(cats),
                    },
                )
                transport.sendto(resp.pack(), addr)
                return

            # Blocklist
            if qname in self.blocklist:
                if self.config.get("telemetry", {}).get("enabled", True):
                    self.telemetry.record_block(cats)
                resp = self._make_response(request, "0.0.0.0")
                self.bus.publish(
                    "dns.block",
                    {
                        "query": qname,
                        "client": client_ip,
                        "reason": "blocklist",
                        "categories": list(cats),
                    },
                )
                transport.sendto(resp.pack(), addr)
                return

            # Default: upstream
            resp = await self._forward_to_upstream(request)
            transport.sendto(resp.pack(), addr)

        except Exception as e:
            print("[DNS] Error handling query:", e)

    async def _forward_to_upstream(self, request: DNSRecord) -> DNSRecord:
        upstream = self.config.get("upstream_resolver", "1.1.1.1")
        try:
            reader, writer = await asyncio.open_connection(upstream, 53)

            packet = request.pack()
            writer.write(len(packet).to_bytes(2, "big") + packet)
            await writer.drain()

            length = int.from_bytes(await reader.readexactly(2), "big")
            response_data = await reader.readexactly(length)

            writer.close()
            await writer.wait_closed()

            return DNSRecord.parse(response_data)

        except Exception as e:
            print("[DNS] Upstream resolver failed:", e)
            return self._make_response(request, "0.0.0.0")

    def _make_response(self, request: DNSRecord, ip: str) -> DNSRecord:
        reply = DNSRecord(
            DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
            q=request.q,
        )
        reply.add_answer(
            RR(
                rname=request.q.qname,
                rtype=QTYPE.A,
                rclass=1,
                ttl=60,
                rdata=A(ip),
            )
        )
        return reply


class DNSProtocol(asyncio.DatagramProtocol):
    def __init__(self, plugin: DNSSinkholePlugin):
        self.plugin = plugin
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.create_task(self.plugin.handle_query(data, addr, self.transport))

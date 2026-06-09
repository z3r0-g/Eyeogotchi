"""
Vulnerability Monitor Plugin (wireframe)
"""

from __future__ import annotations
from typing import Any
from core.system.plugin_base import PluginBase
from core.event_bus.event_bus import EventBus


class VulnerabilityMonitorPlugin(PluginBase):
    name = "vuln_monitor"

    def start(self) -> None:
        print("[VULN] start() called (wireframe)")
        # TODO: gather firmware versions, map to CVEs

    def stop(self) -> None:
        print("[VULN] stop() called (wireframe)")

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "plugin": self.name}


def get_plugin(bus: EventBus) -> VulnerabilityMonitorPlugin:
    return VulnerabilityMonitorPlugin(bus)

"""
Network Mapper Plugin (wireframe)
"""

from __future__ import annotations
from typing import Any
from core.system.extension_base import PluginBase
from core.event_bus.event_bus import EventBus

class NetworkMapperPlugin(PluginBase):
    name = "network_mapper"

    def start(self) -> None:
        print("[MAPPER] start() called (wireframe)")

        # TODO: schedule scans, run nmap, publish events

    def stop(self) -> None:
        print("[MAPPER] stop() called (wireframe)")

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "plugin": self.name}


def get_plugin(bus: EventBus) -> NetworkMapperPlugin:
    return NetworkMapperPlugin(bus)

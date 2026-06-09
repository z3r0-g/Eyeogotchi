"""
IPS Plugin (wireframe)
"""

from __future__ import annotations
from typing import Any
from core.system.extension_base import PluginBase
from core.event_bus.event_bus import EventBus


class IPSPlugin(PluginBase):
    name = "ips"

    def start(self) -> None:
        print("[IPS] start() called (wireframe)")
        # TODO: initialize packet capture, load rules, etc.

    def stop(self) -> None:
        print("[IPS] stop() called (wireframe)")

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "plugin": self.name}


def get_plugin(bus: EventBus) -> IPSPlugin:
    return IPSPlugin(bus)

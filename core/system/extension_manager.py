from __future__ import annotations
from typing import Dict
import logging

from core.system.extension_interface import extension
from core.event_bus.event_bus import EventBus


class ExtensionManager:
    def __init__(self, event_bus: EventBus):
        self.log = logging.getLogger("eyeogotchi.extension_manager")
        self.bus = event_bus
        self._extensions: Dict[str, extension] = {}

    # -------------------------
    # PUBLIC API
    # -------------------------
    def get_extension(self, name: str) -> extension | None:
        return self._extensions.get(name)

    @property
    def extensions(self) -> Dict[str, extension]:
        return self._extensions

    # -------------------------
    # REGISTRATION
    # -------------------------
    def register_extension(self, name: str, ext: extension):
        self._extensions[name] = ext
        self.log.info("Registered extension: %s", name)

        # Optional bridge for display
        runtime = getattr(self.bus, "runtime", None)
        if runtime and name == "display":
            runtime.display_extension = ext

    # -------------------------
    # LIFECYCLE
    # -------------------------
    def start_extension(self, name: str):
        ext = self._extensions.get(name)
        if not ext:
            self.log.warning("Cannot start unknown extension: %s", name)
            return

        self.log.info("Starting extension: %s", name)
        if hasattr(ext, "start"):
            ext.start()
        self.bus.publish("extension.started", {"name": name})

    # -------------------------
    # HEALTH
    # -------------------------
    def health_snapshot(self) -> Dict[str, dict]:
        snapshot = {}
        for name, ext in self._extensions.items():
            if hasattr(ext, "health"):
                try:
                    snapshot[name] = ext.health()
                except Exception as e:
                    snapshot[name] = {"status": "error", "error": str(e)}
            else:
                snapshot[name] = {"status": "unknown"}
        return snapshot

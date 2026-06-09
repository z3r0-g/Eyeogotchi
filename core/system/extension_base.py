# core/system/extension_base.py
from __future__ import annotations
from typing import Any


class ExtensionBase:
    """
    Backwards‑compatible base class for all Eyeogotchi extensions.

    Expected by existing plugins (display, logs, extensions, etc):
      - __init__(runtime)
      - self.runtime
      - self.bus (shared EventBus)
      - self.config (per‑extension config from runtime.config["extensions"][name])
      - self.name (set in subclass)
    """

    # Subclasses should override this
    name: str = "base_extension"

    def __init__(self, runtime):
        # Full runtime object (EyeogotchiRuntime)
        self.runtime = runtime

        # Shared event bus (already created by runtime)
        self.bus = runtime.event_bus

        # Per‑extension config (safe default if missing)
        cfg = {}
        if hasattr(runtime, "config"):
            cfg = runtime.config.get("extensions", {}).get(self.name, {}) or {}
        self.config: dict[str, Any] = cfg

    def start(self) -> None:
        """
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """
        Optional override.
        """
        pass

    def health(self) -> dict[str, Any]:
        """
        Basic health payload; subclasses can extend.
        """
        return {
            "status": "unknown",
            "plugin": self.name,
        }

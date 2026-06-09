# core/system/runtime.py
from __future__ import annotations

import logging
import threading
import time
import random
from typing import Any, Dict, Optional

from core.utils.time_utils import now_unix
from core.config.loader import load_config
from core.config.feature_flags import FeatureFlags
from core.system.extension_loader import ExtensionLoader
from core.system.extension_manager import ExtensionManager
from core.event_bus.event_bus import EventBus
from web.api import create_api
from web.api.server import APIServer


TOP_BANNER_LINES = [
    "Another clue in my dark alley of silicon dreams...",
    "Extensions whisper secrets only I could hear...",
    "Something about this log line SMELLS like trouble...",
    "Every timestamp is a footprint in the fog...",
    "The truth hides between the bytes, kid!",
]

BOTTOM_BANNER_LINES = [
    "I’ve seen stranger STRANGE...",
    "I gotta find this Pepe Silva!",
    "Some logs lie. This one SCREAMS!",
    "Another breadcrumb on the trail ;-P",
    "Eyogotchi never blinks!",
]


class EyeogotchiRuntime:
    def __init__(self):
        self.log = logging.getLogger("eyeogotchi.runtime")

        # Global config from default_config.yaml
        self.config = load_config()

        # Single shared event bus
        self.event_bus: EventBus = EventBus.get()
        self.event_bus.runtime = self

        # Extension system
        self.extension_manager = ExtensionManager(self.event_bus)
        self.extension_loader = ExtensionLoader(self)

        # Discover extensions
        self.extension_meta = self.extension_loader.discover()

        # ------------------------------------------------------------
        # MERGE extension.yaml → runtime.config["extensions"][name]
        # ------------------------------------------------------------
        self._merge_extension_configs()

        # Feature flags AFTER merge
        self.flags = FeatureFlags(self.config.get("extensions", {}))

        self.start_time = now_unix()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_running = False
        self.last_heartbeat: Optional[int] = None
        self.heartbeat_count = 0

        self.api: Optional[APIServer] = None

        # Display / UI state
        self.active_view: tuple[str, Optional[str]] = ("system", None)

        self.wifi_connected: bool = False
        self.bluetooth_on: bool = False
        self.usb_otg: bool = False
        self.ip_shared: bool = False

        self.extension_updates: list[str] = []
        self.extension_updates_owner: Optional[str] = None

        # GLOBAL LOG TAIL
        self.logs_tail: list[str] = []
        self.max_log_lines: int = 200

        # Mascot mood timers
        self.bored_since: Optional[float] = None
        self.casefile_until: Optional[float] = None
        self.casefile_mood: Optional[str] = None
        self.last_case_line: Optional[str] = None

        # Capture all Python logs into logs_tail
        class RuntimeLogHandler(logging.Handler):
            def emit(inner_self, record):
                msg = inner_self.format(record)
                self.add_log_line(msg)

        handler = RuntimeLogHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(handler)

        # Register event handlers
        self._register_event_handlers()

    # ------------------------------------------------------------
    # EXTENSION CONFIG MERGE
    # ------------------------------------------------------------
    def _merge_extension_configs(self):
        """
        Merge extension.yaml settings directly into:
            runtime.config["extensions"][name]
        """
        ext_cfg_root = self.config.setdefault("extensions", {})

        for name, meta in self.extension_meta.items():
            target = ext_cfg_root.setdefault(name, {})

            # enabled flag
            if "enabled" in meta:
                target["enabled"] = meta["enabled"]

            # extension.yaml: settings:
            settings = meta.get("settings", {})
            if isinstance(settings, dict):
                for k, v in settings.items():
                    target[k] = v

            # extension.yaml: config: (legacy)
            config_block = meta.get("config", {})
            if isinstance(config_block, dict):
                for k, v in config_block.items():
                    target[k] = v

    # ------------------------------------------------------------
    # LOG TAIL APPENDER
    # ------------------------------------------------------------
    def add_log_line(self, line: str) -> None:
        if not isinstance(line, str):
            line = str(line)
        self.logs_tail.append(line.strip())
        if len(self.logs_tail) > self.max_log_lines:
            self.logs_tail = self.logs_tail[-self.max_log_lines:]

    # ------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------
    def _register_event_handlers(self) -> None:
        self.event_bus.subscribe("net.wifi.connected", self._on_wifi_connected)
        self.event_bus.subscribe("net.bluetooth.on", self._on_bluetooth_on)
        self.event_bus.subscribe("net.usb.otg", self._on_usb_otg)
        self.event_bus.subscribe("net.ip.shared", self._on_ip_shared)
        self.event_bus.subscribe("display.banner.update", self._on_banner_update)
        self.event_bus.subscribe("ui.navigate", self._on_ui_navigate)
        self.event_bus.subscribe("ui.caseview.line", self._on_caseview_line)

    # Connectivity handlers
    def _on_wifi_connected(self, payload: Any) -> None:
        value = payload.get("connected") if isinstance(payload, dict) else payload
        self.wifi_connected = bool(value)
        self.log.info("WiFi connected: %s", self.wifi_connected)

    def _on_bluetooth_on(self, payload: Any) -> None:
        value = payload.get("on") if isinstance(payload, dict) else payload
        self.bluetooth_on = bool(value)
        self.log.info("Bluetooth on: %s", self.bluetooth_on)

    def _on_usb_otg(self, payload: Any) -> None:
        value = payload.get("plugged") if isinstance(payload, dict) else payload
        self.usb_otg = bool(value)
        self.log.info("USB OTG plugged: %s", self.usb_otg)

    def _on_ip_shared(self, payload: Any) -> None:
        value = payload.get("shared") if isinstance(payload, dict) else payload
        self.ip_shared = bool(value)
        self.log.info("IP shared (DHCP): %s", self.ip_shared)

    # Banner handler
    def _on_banner_update(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self.log.warning("Invalid banner update payload: %r", payload)
            return

        messages = payload.get("messages")
        owner = payload.get("owner")

        if isinstance(messages, list):
            self.extension_updates = [str(m) for m in messages]
        elif isinstance(messages, str):
            self.extension_updates = [messages]
        else:
            self.extension_updates = []

        self.extension_updates_owner = owner
        self.log.info("Banner updated by %s: %s", owner, self.extension_updates)

    # UI navigation
    def _on_ui_navigate(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self.log.warning("Invalid ui.navigate payload: %r", payload)
            return

        view = payload.get("view")

        if view == "system":
            self.active_view = ("system", None)
            self.log.info("Active view set to system")
            return

        if view == "extension":
            ext_name = payload.get("extension")
            if not ext_name:
                self.log.warning("ui.navigate extension view missing 'extension'")
                return
            self.active_view = ("extension", ext_name)
            self.log.info("Active view set to extension: %s", ext_name)
            return

        self.log.warning("Unknown ui.navigate view: %r", view)

    # Case view line handler
    def _on_caseview_line(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self.log.warning("Invalid ui.caseview.line payload: %r", payload)
            return

        line = payload.get("line")
        if not line:
            return

        line = str(line)
        self.last_case_line = line

        now = now_unix()
        if self.casefile_until is None or now >= self.casefile_until:
            self.casefile_until = now + 600

        self._apply_casefile_reaction(line)

    # ------------------------------------------------------------
    # STARTUP
    # ------------------------------------------------------------
    def start(self) -> None:
        self.log.info("Starting Eyeogotchi runtime...")
        self.log.info("Installed Extension Flags: %s", self.flags.all())

        self.event_bus.publish("system.start", {"extensions": self.flags.all()})
        self.extension_loader.load_enabled()

        self.event_bus.publish("system.health", self.extension_manager.health_snapshot())

        self._start_heartbeat(interval=5)
        self._start_api()

    # ------------------------------------------------------------
    # API SERVER
    # ------------------------------------------------------------
    def _start_api(self) -> None:
        app = create_api(self)
        self.api = APIServer(app)
        self.api.start()
        self.log.info("Web API started on port 8080")

    # ------------------------------------------------------------
    # HEARTBEAT LOOP
    # ------------------------------------------------------------
    def _heartbeat_loop(self, interval: int = 5) -> None:
        self.log.info("Heartbeat loop started (interval=%s)", interval)
        while self._heartbeat_running:
            now = now_unix()
            uptime = now - self.start_time
            self.last_heartbeat = now
            self.heartbeat_count += 1

            payload: Dict[str, Any] = {
                "timestamp": now,
                "uptime": uptime,
                "extensions": self.flags.all(),
                "health": self.extension_manager.health_snapshot(),
            }
            self.event_bus.publish("system.heartbeat", payload)

            self._update_casefile_state(now)

            time.sleep(interval)

        self.log.info("Heartbeat loop stopped")

    def _start_heartbeat(self, interval: int = 5) -> None:
        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(interval,),
            daemon=True,
        )
        self._heartbeat_thread.start()

    def _stop_heartbeat(self) -> None:
        self._heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2)

    # ------------------------------------------------------------
    # DETECTIVE MODE HELPERS
    # ------------------------------------------------------------
    def _update_casefile_state(self, now: int) -> None:
        if self.casefile_until is None:
            return

        if now >= self.casefile_until:
            self.casefile_until = None
            self.casefile_mood = None
            self.last_case_line = None
            return

        line = self.last_case_line
        if not line and self.logs_tail:
            line = random.choice(self.logs_tail)

        if not line:
            return

        self._apply_casefile_reaction(line)

    def _apply_casefile_reaction(self, line: str) -> None:
        self.last_case_line = line
        mood = self._classify_log_line(line)
        self.casefile_mood = mood

        top = random.choice(TOP_BANNER_LINES)
        bottom = random.choice(BOTTOM_BANNER_LINES)

        self.event_bus.publish("display.banner.update", {
            "messages": [top, bottom],
            "owner": "mascot",
        })

    def _classify_log_line(self, line: str) -> str:
        text = line.lower()

        if any(k in text for k in ["error", "fail", "timeout"]):
            return "concerned"
        if any(k in text for k in ["wifi down", "disconnect", "disconnected"]):
            return "annoyed"
        if any(k in text for k in ["temp high", "overheat", "overheating"]):
            return "sweating"
        if any(k in text for k in ["cpu spike", "high load", "load="]):
            return "stressed"
        if any(k in text for k in ["handshake", "capture", "pcap"]):
            return "proud"
        if any(k in text for k in ["user", "tap", "interaction", "clicked"]):
            return "excited"

        return "happy"

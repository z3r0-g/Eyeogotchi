# extensions/display/service/main.py
from __future__ import annotations

import logging
import time

from core.event_bus.event_bus import EventBus
from core.display.render import DisplayRenderer
from core.display.views.system_status import build_system_status_view
from core.display.views.extension_status import build_extension_status_view
from core.display.views.case_file import build_case_file_view
from core.mascot.engine import MascotEngine


class DisplayPlugin:
    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger("eyeogotchi.plugin.display")
        self.renderer: DisplayRenderer | None = None

        self.current_view = 0
        self.state = "manual"

        now = time.time()
        self.last_interaction_ts = now
        self.last_rotation_ts = now

        cfg = runtime.config.get("display", {})
        self.pause_seconds = cfg.get("pause_seconds", 30)
        self.rotation_seconds = cfg.get("rotation_seconds", 15)

        self.mascot = MascotEngine(self.runtime)
        setattr(self.runtime, "mascot", self.mascot)

    def get_views(self):
        views = []

        def render_system():
            view = build_system_status_view(self.runtime)
            self.renderer.render_view(view)

        views.append(render_system)

        ext_mgr = self.runtime.extension_manager
        extensions = sorted((getattr(ext_mgr, "_extensions", {}) or {}).keys())

        for ext_name in extensions:
            def render_ext(name=ext_name):
                view = build_extension_status_view(self.runtime, name)
                self.renderer.render_view(view)

            views.append(render_ext)

        return views

    def start(self):
        self.log.info("[DISPLAY] start() called (plugin active)")
        self.renderer = DisplayRenderer()

        setattr(self.runtime, "display", self)

        self.runtime.event_bus.subscribe("system.heartbeat", self.on_heartbeat)
        self.runtime.event_bus.subscribe("touch.double_tap", self.on_double_tap)
        self.runtime.event_bus.subscribe("touch.triple_tap", self.on_triple_tap)

        self.render_active_view()

    def render_active_view(self):
        if not self.renderer:
            return

        if self.current_view < 0:
            ext_index = abs(self.current_view) - 1

            ext_mgr = self.runtime.extension_manager
            extensions = sorted((getattr(ext_mgr, "_extensions", {}) or {}).keys())

            if 0 <= ext_index < len(extensions):
                ext_name = extensions[ext_index]
                view = build_case_file_view(self.runtime, ext_name)
                self.renderer.render_view(view)
                return

            self.current_view = 0

        views = self.get_views()

        if self.current_view >= len(views):
            self.current_view = 0

        views[self.current_view]()

    def on_double_tap(self, payload=None):
        self.log.info("[DISPLAY] Double Tap → rotate views")

        if self.current_view < 0:
            self.current_view = 0
        else:
            self.current_view += 1

        now = time.time()
        self.last_interaction_ts = now
        self.last_rotation_ts = now

        self.state = "manual"
        self.mascot.on_user_interaction()

        self.render_active_view()

    def on_triple_tap(self, payload=None):
        """
        Triple-tap behavior:
          • If on system_status (index 0): ignore
          • If on extension_status (index 1..N): open CASE FILE for that extension
          • If already in CASE FILE (index < 0): ignore
        """

        if self.current_view == 0:
            self.log.info("[DISPLAY] Triple Tap → system view, ignoring")
            return

        if self.current_view < 0:
            self.log.info("[DISPLAY] Triple Tap → already in CASE FILE, ignoring")
            return

        ext_index = self.current_view - 1

        ext_mgr = self.runtime.extension_manager
        extensions = sorted((getattr(ext_mgr, "_extensions", {}) or {}).keys())

        if not (0 <= ext_index < len(extensions)):
            self.log.warning("[DISPLAY] Triple Tap → invalid extension index")
            return

        ext_name = extensions[ext_index]
        self.log.info("[DISPLAY] Triple Tap → opening CASE FILE for: %s", ext_name)

        self.current_view = -(ext_index + 1)

        setattr(self.runtime, "casefile_cursor", 0)
        setattr(self.runtime, "casefile_text", None)

        now = time.time()
        self.last_interaction_ts = now
        self.last_rotation_ts = now
        self.state = "manual"

        self.mascot.on_user_interaction()
        self.render_active_view()

    def on_heartbeat(self, payload):
        now = time.time()
        self.mascot.tick()
        self.mascot.on_idle()

        if self.state == "manual":
            self.state = "pause"
            self.last_interaction_ts = now
            self.render_active_view()
            return

        if self.state == "pause":
            if now - self.last_interaction_ts >= self.pause_seconds:
                self.log.info("[DISPLAY] Pause expired → entering rotation mode")
                self.state = "rotate"
                self.last_rotation_ts = now
            self.render_active_view()
            return

        if self.state == "rotate":
            if now - self.last_rotation_ts >= self.rotation_seconds:
                self.current_view += 1
                self.last_rotation_ts = now
                self.log.info("[DISPLAY] Auto-rotate → next view")

            self.render_active_view()
            return

    def health(self):
        return {
            "status": "ok" if self.renderer else "initializing",
            "view": self.current_view,
            "state": self.state,
        }

    def get_frame_bytes(self):
        if not self.renderer:
            return None
        return self.renderer.get_png_bytes()


def get_plugin(bus: EventBus):
    return DisplayPlugin(bus.runtime)

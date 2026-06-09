import logging
from core.event_bus.event_bus import EventBus

class ExtensionsPlugin:
    """
    Reports installed extensions, but allows excluding certain
    always-on system extensions (e.g., logging, extensions-extension).
    """

    EXCLUDED_EXTENSIONS = {
        "Extensions",     # the extensions-extension itself
        "Logs",           # logging extension
    }

    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger("eyeogotchi.plugin.extensions")

    def start(self):
        self.log.info("[EXTENSIONS] start() called")

    def health(self):
        return {"status": "ok"}

    # ------------------------------------------------------------
    # NEW: Filtered extension listing
    # ------------------------------------------------------------
    def list_extensions(self):
        """
        Returns a filtered list of extensions from the extension manager.
        Excludes system extensions defined in EXCLUDED_EXTENSIONS.
        """
        pm = self.runtime.extension_manager

        visible = {
            name: ext
            for name, ext in pm.extensions.items()
            if name not in self.EXCLUDED_EXTENSIONS
        }

        return visible

    # ------------------------------------------------------------
    # Entrypoint for loader
    # ------------------------------------------------------------
    def get_plugin(bus: EventBus):
        return ExtensionsPlugin(bus.runtime)

import logging
from core.system.plugin_interface import Plugin

class TemplateExtension(Plugin):
    def __init__(self, bus, config):
        self.bus = bus
        self.config = config
        self.log = logging.getLogger("eyeogotchi.template")

    def start(self):
        self.log.info("TemplateExtension started")
        self.log.info(f"Configured message: {self.config.get('message')}")

    def stop(self):
        self.log.info("TemplateExtension stopped")

    def health(self):
        return {
            "status": "ok",
            "message": self.config.get("message")
        }

def get_plugin(bus):
    config = bus.runtime.config.get("template", {})
    return TemplateExtension(bus, config)

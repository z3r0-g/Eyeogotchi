import logging
from core.event_bus.event_bus import EventBus

class LogsPlugin:
    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger("eyeogotchi.plugin.logs")

    def start(self):
        self.log.info("[LOGS] start() called")

    def health(self):
        return {"status": "ok"}

def get_plugin(bus: EventBus):
    return LogsPlugin(bus.runtime)

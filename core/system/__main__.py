import logging
import time
from core.logging.setup import setup_logging
from core.system.runtime import EyeogotchiRuntime
from core.event_bus.event_bus import EventBus

def main():
    setup_logging()
    bus = EventBus.get()
    bus.subscribe("system.start", lambda payload: print(f"System started with modules: {payload['modules']}"))
    bus.subscribe("system.heartbeat", lambda p: print("[HEARTBEAT]", p["uptime"]))

    runtime = EyeogotchiRuntime()
    runtime.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()

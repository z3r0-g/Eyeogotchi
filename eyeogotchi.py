from core.logging.setup import setup_logging
from core.config.loader import load_config
from core.system.runtime import EyeogotchiRuntime
from web.api import create_api
from web.api.server import APIServer
import logging

def main():
    config = load_config()
    setup_logging(config)
    logging.info("Eyeogotchi Opening a Case!")

    runtime = EyeogotchiRuntime()
    runtime.start()  # starts heartbeat + extensions in background

    app = create_api(runtime)

    server = APIServer(app)
    server.start()

if __name__ == "__main__":
    main()

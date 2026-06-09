import logging
import logging.handlers
import os

BASE_DIR = os.path.expanduser("~/.eyeogotchi/logs")
LOGFILE = os.path.join(BASE_DIR, "eyeogotchi.log")

def setup_logging(config):
    # Ensure directory exists
    os.makedirs(BASE_DIR, exist_ok=True)

    # Read level from config
    level_name = config.get("logging", {}).get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        LOGFILE,
        maxBytes=2_000_000,   # 2 MB
        backupCount=3
    )
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Console output (helpful during dev)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    logging.info(f"Logging initialized at level {level_name}")

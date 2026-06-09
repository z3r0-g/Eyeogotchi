from flask import Blueprint, current_app

config_bp = Blueprint("config", __name__, url_prefix="/config")

@config_bp.get("/")
def config():
    # Return only safe config keys
    cfg = current_app.runtime.config.copy()
    cfg.pop("secrets", None)
    return cfg

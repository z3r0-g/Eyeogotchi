from flask import Blueprint, current_app

health_bp = Blueprint("health", __name__, url_prefix="/health")

@health_bp.get("/")
def health():
    return current_app.runtime.health_snapshot()

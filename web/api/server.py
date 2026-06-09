# web/api/server.py
from flask import Blueprint

from web.api.routes.health import health_bp
from web.api.routes.logs import logs_bp
from web.api.routes.extensions import extensions_bp
from web.api.routes.config import config_bp
from web.api.routes.display import display_bp

# Root API blueprint (not strictly needed if you use create_api, but harmless)
api = Blueprint("api", __name__)
api.register_blueprint(logs_bp)
api.register_blueprint(health_bp)
api.register_blueprint(extensions_bp)
api.register_blueprint(config_bp)
api.register_blueprint(display_bp)


class APIServer:
    def __init__(self, app):
        self.app = app

    def start(self):
        # Blocking dev server; runtime already runs heartbeat in a thread
        self.app.run(host="0.0.0.0", port=8080, threaded=True)

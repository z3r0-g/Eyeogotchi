# web/api/__init__.py
from flask import Flask
from web import ui_bp

from web.api.routes.extensions import extensions_bp
from web.api.routes.health import health_bp
from web.api.routes.logs import logs_bp
from web.api.routes.config import config_bp
from web.api.routes.display import display_bp


def create_api(runtime):
    # Disable Flask's own static handling; we use blueprints + extension loader
    app = Flask(__name__, static_folder=None)
    app.runtime = runtime

    # CORE API ROUTES
    app.register_blueprint(display_bp, url_prefix="/api/display")
    app.register_blueprint(extensions_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(logs_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api")

    # EXTENSION STATIC + API ROUTES
    runtime.extension_loader.register_api(app)

    # UI ROUTES (index + core static)
    app.register_blueprint(ui_bp)

    return app

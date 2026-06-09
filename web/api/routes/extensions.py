#web/api/routes/extensions.py
from flask import Blueprint, jsonify, current_app

extensions_bp = Blueprint("extensions", __name__)

@extensions_bp.get("/extensions/")
def list_extensions():
    runtime = current_app.runtime

    # extension_meta comes from ExtensionLoader.discover()
    meta = getattr(runtime, "extension_meta", {}) or {}

    extensions = []
    for name, info in meta.items():
        enabled = info.get("enabled", False)

        # plugin instance if loaded
        plugin = runtime.extension_manager.extensions.get(name)

        # simple pass/fail health
        if plugin and hasattr(plugin, "health"):
            health = plugin.health().get("status", "unknown")
        else:
            health = "unknown"

        extensions.append({
            "name": name,
            "label": info.get("label", name.title()),
            "description": info.get("description", ""),
            "enabled": enabled,
            "version": info.get("version", "0.0.0"),
            "status": health,
        })

    return jsonify({"extensions": extensions})

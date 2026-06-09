from flask import Blueprint, current_app

# IMPORTANT: the blueprint name MUST be "display"
# because Flask uses this internally and your API loader expects display_bp
display_bp = Blueprint("display", __name__)

# ------------------------------------------------------------
# FRAME ENDPOINT
# ------------------------------------------------------------
@display_bp.route("/frame", methods=["GET"])
def get_frame():
    runtime = current_app.runtime
    plugin = runtime.extension_manager.get_extension("display")

    if not plugin:
        return "Display plugin not loaded", 503

    data = plugin.get_frame_bytes()
    if not data:
        return "Display not initialized", 503

    return current_app.response_class(data, mimetype="image/png")

# ------------------------------------------------------------
# TOUCH SIMULATION
# ------------------------------------------------------------
@display_bp.route("/simulate_double_tap", methods=["POST"])
def simulate_double_tap():
    runtime = current_app.runtime
    runtime.event_bus.publish("touch.double_tap", {})
    return {"status": "ok"}

@display_bp.route("/simulate_triple_tap", methods=["POST"])
def simulate_triple_tap():
    runtime = current_app.runtime
    runtime.event_bus.publish("touch.triple_tap", {})
    return {"status": "ok"}

# ------------------------------------------------------------
# POWER CONTROLS
# ------------------------------------------------------------
@display_bp.route("/shutdown", methods=["POST"])
def simulate_shutdown():
    print("[DEV] Shutdown requested")
    return {"status": "shutting_down"}

@display_bp.route("/reboot", methods=["POST"])
def simulate_reboot():
    print("[DEV] Reboot requested")
    return {"status": "rebooting"}

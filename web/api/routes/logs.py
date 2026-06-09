from flask import Blueprint, Response, current_app
import os

logs_bp = Blueprint("logs", __name__)

@logs_bp.get("/logs/")
def logs():
    # Prefer runtime.log_file_path if set, otherwise fall back to LOGFILE constant
    runtime = getattr(current_app, "runtime", None)
    log_path = getattr(runtime, "log_file_path", None)

    if not log_path:
        # Fallback to old hardcoded path if you still want it
        from core.logging.setup import LOGFILE as DEFAULT_LOGFILE
        log_path = DEFAULT_LOGFILE

    if not os.path.exists(log_path):
        return Response(f"No Logs Written to {log_path}", mimetype="text/plain")

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-200:]  # tail last 200 lines

    return Response("".join(lines), mimetype="text/plain")

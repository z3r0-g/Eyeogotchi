# core/display/views/system_status.py
from __future__ import annotations

import psutil
import time

from core.display.view_model import ViewModel, GridCell


def format_seconds(sec: int) -> str:
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60

    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def build_system_status_view(runtime) -> ViewModel:
    mascot_state = runtime.mascot.get_sprite_for_state()

    uptime_seconds = int(time.time() - runtime.start_time)
    uptime_str = format_seconds(uptime_seconds)

    hb_ts = runtime.last_heartbeat or runtime.start_time
    hb_age = int(time.time() - hb_ts)
    hb_str = format_seconds(hb_age)

    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    ram = mem.percent

    temp = None
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            first = next(iter(temps.values()))
            if first:
                temp = first[0].current
    except Exception:
        temp = None

    temp_str = f"{temp:.0f}°C" if temp is not None else "N/A"

    ext_mgr = runtime.extension_manager
    ext_dict = getattr(ext_mgr, "extensions", {}) or {}
    ext_count = len(ext_dict)

    # ------------------------------------------------------------
    # LEFT GRID (with icons + EXT badge)
    # ------------------------------------------------------------
    left_grid = [
        GridCell(icon="cpu", value=f"{cpu:.0f}%"),
        GridCell(icon="ram", value=f"{ram:.0f}%"),

        GridCell(icon="temp", value=temp_str),
        GridCell(icon="ext", value=f"{ext_count:02d}"),

        GridCell(icon="up", value=uptime_str),
        GridCell(icon="hb", value=f"{runtime.heartbeat_count:03d}"),
    ]

    # ------------------------------------------------------------
    # RIGHT GRID (connectivity icons)
    # ------------------------------------------------------------
    wifi = getattr(runtime, "wifi_connected", False)
    bt = getattr(runtime, "bluetooth_on", False)
    usb = getattr(runtime, "usb_otg", False)
    share = getattr(runtime, "ip_shared", False)

    right_grid = [
        GridCell(icon="wifi", enabled=wifi),
        GridCell(icon="bt", enabled=bt),

        GridCell(icon="usb", enabled=usb),
        GridCell(icon="share", enabled=share),

        GridCell(text="", value=""),
        GridCell(text="", value=""),
    ]

    # ------------------------------------------------------------
    # Banner text (safe rotation)
    # ------------------------------------------------------------
    updates = getattr(runtime, "extension_updates", None)
    if not updates:
        updates = ["[ No News!  (o_o)  ]"]

    banner_text = updates[uptime_seconds % len(updates)]

    return ViewModel(
        title="EYEOGOTCHI",
        mascot_state=mascot_state,  # ✔ now a string, not a dict
        left_grid=left_grid,
        right_grid=right_grid,
        banner_text=banner_text,
    )

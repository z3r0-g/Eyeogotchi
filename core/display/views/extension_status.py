# core/display/views/extension_status.py
from __future__ import annotations

from core.display.view_model import ViewModel, GridCell

def build_extension_status_view(runtime, ext_name: str) -> ViewModel:
    ext_mgr = runtime.extension_manager
    ext = getattr(ext_mgr, "_extensions", {}).get(ext_name)

    # Mascot reaction engine
    mascot_state = runtime.mascot.get_sprite_for_state()

    # ------------------------------------------------------------
    # EXTENSION METADATA (from extension.yaml)
    # ------------------------------------------------------------
    meta = runtime.extension_meta.get(ext_name, {})

    version = meta.get("version") or getattr(ext, "version", "—")
    desc = meta.get("description", "No description provided")

    # Health (only meaningful status)
    try:
        health = ext.health().get("status", "N/A") if ext else "N/A"
    except Exception:
        health = "N/A"

    # ------------------------------------------------------------
    # LEFT GRID (2×3)
    # ------------------------------------------------------------
    left_grid = [
        GridCell(text="VER", value=version),
        GridCell(text="HLTH", value=health),

        GridCell(text="ICON3", value="3"),
        GridCell(text="ICON4", value="4"),

        GridCell(text="ICON5", value="5"),
        GridCell(text="ICON6", value="6"),
    ]

    # ------------------------------------------------------------
    # RIGHT GRID (empty for now)
    # ------------------------------------------------------------
    right_grid = [
        GridCell(text="", value=""),
        GridCell(text="", value=""),

        GridCell(text="", value=""),
        GridCell(text="", value=""),

        GridCell(text="", value=""),
        GridCell(text="", value=""),
    ]

    # HEADER + FOOTER
    title = f"<EXT://> {ext_name}"
    banner_text = desc 

    return ViewModel(
        title=title,
        mascot_state=mascot_state,
        left_grid=left_grid,
        right_grid=right_grid,
        banner_text=banner_text,
    )

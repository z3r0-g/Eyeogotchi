# core/display/views/case_file.py
from __future__ import annotations
from core.display.view_model import ViewModel, GridCell


# ------------------------------------------------------------
# Helper: partner name from config (safe fallback)
# ------------------------------------------------------------
def _get_partner_name(runtime) -> str:
    cfg = getattr(runtime, "base_config", None) or getattr(runtime, "config", None)
    if isinstance(cfg, dict):
        return cfg.get("partner", "Detective")
    return "Detective"


# ------------------------------------------------------------
# Helper: filter logs for this extension only
# ------------------------------------------------------------
def _filter_logs(runtime, ext_name: str) -> list[str]:
    logs = getattr(runtime, "logs_tail", None)
    if not logs:
        return []

    tag = f"[{ext_name.upper()}]"
    return [line for line in logs if tag in line]


# ------------------------------------------------------------
# Helper: infer mascot sprite from log content
# ------------------------------------------------------------
def _infer_sprite_from_log(line: str) -> str:
    lower = line.lower()

    if "error" in lower or "failed" in lower:
        return "concerned"
    if "start()" in lower or "registered" in lower:
        return "proud"
    if "get /api" in lower:
        return "curious"
    if "double tap" in lower or "triple tap" in lower:
        return "excited"
    if "wifi" in lower and "down" in lower:
        return "annoyed"

    return "happy"


# ------------------------------------------------------------
# Build case text + inferred mascot sprite
# ------------------------------------------------------------
def _build_case_text(runtime, ext_name: str) -> tuple[str, str]:
    partner = _get_partner_name(runtime)
    filtered = _filter_logs(runtime, ext_name)

    if filtered:
        # Last 3 log lines for this extension
        last_three = "\n".join(line.strip() for line in filtered[-3:])
        sprite = _infer_sprite_from_log(filtered[-1])

        text = (
            f"{partner},\n\n"
            "Recent Activity Includes:\n"
            f"{last_three}"
        )
        return text, sprite

    # No logs for this extension
    text = (
        f"{partner},\n\n"
        "No recent activity recorded.\n"
        "The trail's gone cold... for now."
    )
    return text, "bored"


# ------------------------------------------------------------
# Build the CASE FILE view
# ------------------------------------------------------------
def build_case_file_view(runtime, ext_name: str) -> ViewModel:
    case_text, inferred_sprite = _build_case_text(runtime, ext_name)

    # Use inferred sprite ONLY if it exists in assets
    mascot = runtime.mascot
    if mascot and hasattr(mascot, "sprite_exists") and mascot.sprite_exists(inferred_sprite):
        mascot_state = inferred_sprite
    else:
        mascot_state = mascot.get_sprite_for_state()

    right_grid = [
        GridCell(text="ICON1", value="1"),
        GridCell(text="ICON2", value="2"),
    ]

    return ViewModel(
        title=f"CASE FILE: {ext_name}",
        mascot_state=mascot_state,
        left_grid=[],
        right_grid=right_grid,
        banner_text=None,
        case_text=case_text,
        case_layout="case_file",
    )

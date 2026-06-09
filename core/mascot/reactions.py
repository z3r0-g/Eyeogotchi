#core/mascot/reactions.py
from __future__ import annotations
import time
import random


def compute_mascot_state(runtime) -> str:
    """
    Decides mascot state based on runtime metrics for moods:
    annoyed, curious, stressed, bored, excited, proud, sweating,
    concerned, happy, sleeping
    """

    # Default fallback
    state = "sleeping"

    now = time.time()
    last_hb = runtime.last_heartbeat or runtime.start_time
    idle_seconds = max(0, int(now - last_hb))

    # Runtime metrics (safe fallbacks)
    cpu = getattr(runtime, "last_cpu", None)
    temp = getattr(runtime, "last_temp", None)
    wifi = getattr(runtime, "wifi_connected", True)
    errors = getattr(runtime, "recent_error_count", 0)

    # Optional event hook (extensions can set this)
    last_event = getattr(runtime, "last_event", None)

    # ------------------------------------------------------------
    # HIGH‑PRIORITY STATES (override everything else)
    # ------------------------------------------------------------

    # System errors → concerned
    if errors and errors > 0:
        return "concerned"

    # Overheating → sweating
    if temp is not None and temp > 60:
        return "sweating"

    # CPU overload → stressed
    if cpu is not None and cpu > 80:
        return "stressed"

    # No WiFi → annoyed
    if not wifi:
        return "annoyed"

    # ------------------------------------------------------------
    # MID‑PRIORITY STATES (event‑driven reactions)
    # ------------------------------------------------------------

    # These are short‑lived moods triggered by events.
    # Extensions can set runtime.last_event = "handshake", etc.

    if last_event == "handshake":
        return "proud"

    if last_event == "user_interaction":
        return "excited"

    if last_event == "new_ap":
        return "curious"

    # ------------------------------------------------------------
    # DETECTIVE MODE (case‑file reading)
    # ------------------------------------------------------------

    casefile_until = getattr(runtime, "casefile_until", None)
    casefile_mood = getattr(runtime, "casefile_mood", None)

    if casefile_until is not None and now < casefile_until and casefile_mood:
        # In active detective mode: use mood derived from log lines
        return casefile_mood

    # If detective window expired, clear state
    if casefile_until is not None and now >= casefile_until:
        runtime.casefile_until = None
        runtime.casefile_mood = None
        runtime.last_case_line = None

    # ------------------------------------------------------------
    # LOW‑PRIORITY STATES (ambient moods)
    # ------------------------------------------------------------

    # Idle too long → bored, then curious after 300s of boredom,
    # which also starts detective mode (case‑file reading).
    if idle_seconds > 300:
        if getattr(runtime, "bored_since", None) is None:
            runtime.bored_since = now

        bored_duration = now - runtime.bored_since

        # After 300 seconds of being bored → curious + start detective mode
        if bored_duration >= 300:
            if getattr(runtime, "casefile_until", None) is None or now >= runtime.casefile_until:
                runtime.casefile_until = now + 600  # 600s detective window
                runtime.casefile_mood = "curious"
            return "curious"

        # Still in initial boredom phase
        return "bored"

    # Reset boredom timer when not bored
    runtime.bored_since = None

    # Lightly warm → sweating (mild)
    if temp is not None and 50 < temp <= 60:
        return "sweating"

    # Light CPU load → happy
    if cpu is not None and 20 < cpu <= 50:
        return "happy"

    # Very low activity → sleeping
    if idle_seconds > 120:
        return "sleeping"

    # Default ambient mood
    return "sleeping"

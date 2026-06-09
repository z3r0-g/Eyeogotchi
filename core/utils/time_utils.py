# core/utils/time_utils.py
"""
Time utilities for Eyeogotchi.
"""

from __future__ import annotations
import time
from datetime import datetime, timezone


def now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def now_unix() -> int:
    """Return current UNIX timestamp."""
    return int(time.time())


def since(start_ts: float) -> float:
    """Return seconds elapsed since a given timestamp."""
    return time.time() - start_ts

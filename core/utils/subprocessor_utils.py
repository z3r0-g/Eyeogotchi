"""
Safe subprocess wrapper for Eyeogotchi.

Prevents blocking, captures output, and logs failures.
"""

from __future__ import annotations
import subprocess
import logging
from typing import List, Tuple

log = logging.getLogger("eyeogotchi.subprocess_utils")


def run(cmd: List[str], timeout: float = 5.0) -> Tuple[int, str, str]:
    """
    Run a subprocess safely.
    Returns (exit_code, stdout, stderr).
    """
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout.strip(), stderr.strip()

    except subprocess.TimeoutExpired:
        proc.kill()
        log.error(f"Command timed out: {cmd}")
        return -1, "", "timeout"

    except Exception as e:
        log.error(f"Subprocess failed: {cmd} -> {e}")
        return -1, "", str(e)

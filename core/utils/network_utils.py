"""
Network utilities for Eyeogotchi.
"""

from __future__ import annotations
import socket
import fcntl
import struct
import logging

log = logging.getLogger("eyeogotchi.network_utils")


def get_ip_address(ifname: str) -> str | None:
    """
    Return the IPv4 address for a given interface.
    Works on Linux; returns None on failure.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", ifname[:15].encode("utf-8"))
            )[20:24]
        )
    except Exception as e:
        log.debug(f"Failed to get IP for {ifname}: {e}")
        return None


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """Return True if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

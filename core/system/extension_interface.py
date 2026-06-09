# core/system/extension_interface.py
# Extension Interface for Eyeogotchi extensions.
# For now, we also support legacy extensions that only expose main().

from __future__ import annotations
from typing import Protocol, Any


class extension(Protocol):
    """
    Basic extension interface.

    TODO:
    - Extend with async hooks if needed
    - Add metadata (version, description, capabilities)
    """

    name: str

    def start(self) -> None:
        """Start the extension's main behavior."""
        ...

    def stop(self) -> None:
        """Stop the extension and clean up resources."""
        ...

    def health(self) -> dict[str, Any]:
        """Return a health/status snapshot."""
        ...

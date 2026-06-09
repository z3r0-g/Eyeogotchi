"""
Usage:
    from core.event_bus.event_bus import EventBus

    bus = EventBus.get()

    def handler(payload):
        print("Got event:", payload)

    bus.subscribe("lte.metrics", handler)
    bus.publish("lte.metrics", {"rsrp": -95})
"""

from __future__ import annotations
from typing import Callable, Dict, List, Any
import logging
import threading


class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.log = logging.getLogger("eyeogotchi.event_bus")
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    # -----------------------------
    # Singleton Accessor
    # -----------------------------
    @classmethod
    def get(cls) -> "EventBus":
        with cls._lock:
            if cls._instance is None:
                cls._instance = EventBus()
            return cls._instance

    # -----------------------------
    # Subscription
    # -----------------------------
    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """
        Register a handler for a specific event type.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)
        self.log.debug(f"Subscribed handler {handler.__name__} to event '{event_type}'")

    # -----------------------------
    # Publishing
    # -----------------------------
    def publish(self, event_type: str, payload: Any) -> None:
        """
        Publish an event to all subscribers.
        """
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            self.log.debug(f"No subscribers for event '{event_type}'")
            return

        self.log.debug(f"Publishing event '{event_type}' to {len(handlers)} handlers")

        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                self.log.error(
                    f"Handler '{handler.__name__}' failed for event '{event_type}': {e}"
                )

from collections import defaultdict
from typing import Callable, Any

_subscribers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

def subscribe(event_type: str, handler: Callable[[Any], None]) -> None:
    _subscribers[event_type].append(handler)

def publish(event_type: str, payload: Any) -> None:
    for handler in _subscribers.get(event_type, []):
        # TODO: consider try/except and logging
        handler(payload)

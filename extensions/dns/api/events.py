# extensions/dns/api/events.py
import time
from collections import deque

# Shared ring buffer
_DNS_EVENTS = deque(maxlen=500)

def record_dns_event(event: dict):
    """
    Called by event-bus subscribers.
    """
    event = dict(event)
    event["timestamp"] = event.get("timestamp", time.time())
    _DNS_EVENTS.appendleft(event)

def get_dns_events(limit: int = 100):
    return list(_DNS_EVENTS)[:limit]

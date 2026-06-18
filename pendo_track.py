"""
DealDesk AI — Pendo server-side Track Event utility
Sends events to the Pendo Track API for analytics.
"""

import time
import requests

PENDO_TRACK_URL = "https://data.pendo.io/data/track"
PENDO_INTEGRATION_KEY = "78c408b3-e761-4880-806f-189796aeb561"


def track_event(event_name, properties=None, visitor_id="system", account_id="system"):
    """Send a track event to Pendo. Failures are silently ignored."""
    try:
        payload = {
            "type": "track",
            "event": event_name,
            "visitorId": visitor_id,
            "accountId": account_id,
            "timestamp": int(time.time() * 1000),
        }
        if properties:
            payload["properties"] = properties
        requests.post(
            PENDO_TRACK_URL,
            headers={
                "Content-Type": "application/json",
                "x-pendo-integration-key": PENDO_INTEGRATION_KEY,
            },
            json=payload,
            timeout=5,
        )
    except Exception:
        pass

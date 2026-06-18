"""
DealDesk AI — Band Agent API client
Each of the 5 agents authenticates with its own agent key and posts to a shared chat room.

Base URL:  https://app.band.ai/api/v1/agent
Auth:      X-API-Key: band_a_...   (one key per agent)
"""

import hashlib
import time
import requests
from config import (
    BAND_RESEARCH_KEY, BAND_RISK_KEY, BAND_VALUATION_KEY,
    BAND_WRITER_KEY, BAND_HUMANREVIEW_KEY,
)

BASE_URL = "https://app.band.ai/api/v1/agent"

# ── Fixed UUIDs assigned by Band after registration ──────────────────────────
AGENT_IDS = {
    "@Research":    "19d9532d-c460-4b14-8ab8-27834dc17e1b",
    "@Risk":        "164a10ce-84e3-4eca-8d70-9d4c63cf842e",
    "@Valuation":   "673c7f8b-3eb4-4b5d-955b-2a94d1367d59",
    "@Writer":      "60f69da5-1b9d-4478-843f-72e9e5abc22b",
    "@HumanReview": "05611ec7-7f33-4bd3-a6a5-8a1f30e70c44",
}

AGENT_KEYS = {
    "@Research":    BAND_RESEARCH_KEY,
    "@Risk":        BAND_RISK_KEY,
    "@Valuation":   BAND_VALUATION_KEY,
    "@Writer":      BAND_WRITER_KEY,
    "@HumanReview": BAND_HUMANREVIEW_KEY,
}

# Human owner ID (jhontejada95) — needed for mentions when no agent follows
USER_ID = "5e33c5e2-ae9d-444f-905b-d076a8699f80"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headers(agent: str) -> dict:
    return {
        "X-API-Key": AGENT_KEYS[agent],
        "Content-Type": "application/json",
    }


# ── Chat management ───────────────────────────────────────────────────────────

def create_chat(title: str, creator: str = "@Research") -> str:
    """Create a Band chat room and add all 5 agents + human owner."""
    resp = requests.post(
        f"{BASE_URL}/chats",
        headers=_headers(creator),
        json={"chat": {"title": title}},
    )
    if not resp.ok:
        print(f"[Band] Create chat failed ({resp.status_code}): {resp.text}")
        return _fallback_chat_id(title)

    chat_id = resp.json()["data"]["id"]
    print(f"[Band] ✅ Chat room created: {chat_id}")
    _add_all_participants(chat_id, creator)
    return chat_id


def _add_all_participants(chat_id: str, creator: str):
    """Add all sibling agents and the human owner as participants."""
    creator_id = AGENT_IDS[creator]
    to_add = [(name, uid) for name, uid in AGENT_IDS.items() if uid != creator_id]
    to_add.append(("@User (human)", USER_ID))

    for name, uid in to_add:
        resp = requests.post(
            f"{BASE_URL}/chats/{chat_id}/participants",
            headers=_headers(creator),
            json={"participant": {"participant_id": uid}},
        )
        icon = "✅" if resp.ok else f"⚠️ ({resp.status_code})"
        print(f"[Band]   {icon} {name}")


# ── Messaging ─────────────────────────────────────────────────────────────────

def send_message(chat_id: str, sender: str, content: str,
                 mention_next: str = None) -> bool:
    """
    Post a message as `sender` agent.
    If `mention_next` is given, that agent is @mentioned (triggers its webhook).
    Falls back to mentioning the human owner when no next agent exists.
    """
    if mention_next and mention_next in AGENT_IDS:
        mentions = [{"id": AGENT_IDS[mention_next]}]
    else:
        mentions = [{"id": USER_ID}]   # Band requires ≥1 mention

    resp = requests.post(
        f"{BASE_URL}/chats/{chat_id}/messages",
        headers=_headers(sender),
        json={"message": {"content": content, "mentions": mentions}},
    )
    if not resp.ok:
        print(f"[Band] ⚠️  Message from {sender} failed ({resp.status_code}): {resp.text[:200]}")
        return False
    return True


# ── Health check ──────────────────────────────────────────────────────────────

def verify_connection() -> bool:
    """Confirm the Research agent key is valid."""
    resp = requests.get(f"{BASE_URL}/me", headers=_headers("@Research"))
    if resp.status_code == 200:
        print("[Band] ✅ Connected — Agent API active")
        return True
    print(f"[Band] ⚠️  API check failed ({resp.status_code}). Running in offline mode.")
    return False


# ── Offline fallback ──────────────────────────────────────────────────────────

def _fallback_chat_id(title: str) -> str:
    session_id = hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12]
    print(f"[Band] Running offline. Session ID: {session_id}")
    return f"local-{session_id}"

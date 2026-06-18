"""
DealDesk AI — Configuration
Loads credentials from .env file. Never hard-code keys here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Featherless AI (LLM, OpenAI-compatible) ───────────────────────────────────
FEATHERLESS_API_KEY  = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
LLM_MODEL            = "Qwen/Qwen2.5-72B-Instruct"

# ── Band Agent API keys (one per registered remote agent) ─────────────────────
BAND_RESEARCH_KEY    = os.getenv("BAND_RESEARCH_KEY", "")
BAND_RISK_KEY        = os.getenv("BAND_RISK_KEY", "")
BAND_VALUATION_KEY   = os.getenv("BAND_VALUATION_KEY", "")
BAND_WRITER_KEY      = os.getenv("BAND_WRITER_KEY", "")
BAND_HUMANREVIEW_KEY = os.getenv("BAND_HUMANREVIEW_KEY", "")

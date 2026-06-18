"""
DealDesk AI — LLM wrapper
Uses Featherless AI (OpenAI-compatible) with Qwen2.5-72B.
"""

from openai import OpenAI
from config import FEATHERLESS_API_KEY, FEATHERLESS_BASE_URL, LLM_MODEL

_client = OpenAI(api_key=FEATHERLESS_API_KEY, base_url=FEATHERLESS_BASE_URL)


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    """Call Featherless AI and return the response text."""
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

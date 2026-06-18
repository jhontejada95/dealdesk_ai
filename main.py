"""
DealDesk AI — Main orchestrator
Band of Agents Hackathon 2026

5 AI agents coordinate through a Band chat room to produce
an investment-grade due diligence memo with human-in-the-loop approval.

Each agent posts its output to Band using its own Agent API key and
@mentions the next agent in the pipeline — creating a live, auditable
conversation visible in the Band UI.

Usage:
    python main.py
"""

import json
from datetime import datetime
from band_client import create_chat, send_message, verify_connection
from agents import (
    agent_research,
    agent_risk,
    agent_valuation,
    agent_writer,
    agent_human_review,
)

# Pipeline order for @mention routing
PIPELINE = ["@Research", "@Risk", "@Valuation", "@Writer", "@HumanReview"]


def save_report(company: str, memo: str, verdict: str, chat_id: str, transcript: list):
    """Save the final memo and full agent transcript to JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = company.lower().replace(" ", "_")
    filename = f"dealdesk_{slug}_{timestamp}.json"

    report = {
        "company": company,
        "timestamp": timestamp,
        "band_chat_id": chat_id,
        "band_chat_url": f"https://app.band.ai/chats/{chat_id}",
        "investment_memo": memo,
        "human_verdict": verdict,
        "agent_transcript": transcript,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Report saved → {filename}")
    return filename


def run_dealdesk():
    print("=" * 60)
    print("  🏦 DealDesk AI — M&A Due Diligence System")
    print("  5 AI Agents · Band Coordination · Human-in-the-Loop")
    print("=" * 60)

    # ── Verify Band connection ────────────────────────────────
    band_online = verify_connection()

    # ── Get target company ───────────────────────────────────
    company = input("\nCompany to analyze: ").strip()
    if not company:
        company = "Acme Corp"

    print("Additional context (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    context = "\n".join(lines).strip() or "No additional context provided."

    # ── Create Band chat room with all 5 agents ───────────────
    chat_id = create_chat(f"DealDesk AI — {company} Due Diligence")
    transcript = []

    def log(agent: str, content: str, mention_next: str = None):
        """Post to Band as this agent, mention the next one, keep local transcript."""
        transcript.append({"agent": agent, "content": content})
        if band_online and not chat_id.startswith("local-"):
            send_message(chat_id, agent, content, mention_next)

    # ── Kickoff message ───────────────────────────────────────
    kickoff = (
        f"🚀 **DealDesk AI** session started\n"
        f"**Target:** {company}\n"
        f"**Pipeline:** Research → Risk → Valuation → Writer → HumanReview\n"
        f"**Context:** {context[:300]}{'...' if len(context) > 300 else ''}"
    )
    log("@Research", kickoff, mention_next="@Risk")

    # ── Agent pipeline ────────────────────────────────────────
    research  = agent_research(company, context,              log)
    risk      = agent_risk(research,                          log)
    valuation = agent_valuation(research, risk,               log)
    memo      = agent_writer(company, research, risk, valuation, log)
    verdict   = agent_human_review(memo,                      log)

    # ── Save & summarize ─────────────────────────────────────
    filename = save_report(company, memo, verdict, chat_id, transcript)

    print("\n" + "=" * 60)
    print(f"✅ Done — {company}")
    print(f"   Verdict  : {verdict[:80]}")
    print(f"   Band     : https://app.band.ai/chats/{chat_id}")
    print(f"   Report   : {filename}")
    print("=" * 60)


if __name__ == "__main__":
 
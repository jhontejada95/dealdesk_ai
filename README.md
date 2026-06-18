# 🏦 DealDesk AI

> **5 AI agents that collaborate in real time to produce investment-grade M&A due diligence — with a human in the loop.**

Built for the [Band of Agents Hackathon](https://lablab.ai) · Powered by [Band](https://band.ai) + [Featherless AI](https://featherless.ai)

---

## What it does

DealDesk AI takes a target company name and produces a complete investment memo in minutes. Five specialized AI agents coordinate through a **Band chat room**, each posting their analysis and @mentioning the next agent — creating a live, auditable conversation you can watch unfold in real time.

The pipeline ends with a **human-in-the-loop gate**: a human reviewer reads the full memo and decides to APPROVE, REJECT, or REQUEST CHANGES before anything moves forward.

---

## Agent Pipeline

```
User Input
    │
    ▼
@Research ──→ @Risk ──→ @Valuation ──→ @Writer ──→ @HumanReview ──→ Final Verdict
```

| Agent | Role |
|---|---|
| **@Research** | Senior investment analyst. Researches business model, financials, team, competitors, market signals. |
| **@Risk** | Due diligence specialist. Identifies business, team, financial, and regulatory risks. Scores LOW / MEDIUM / HIGH. |
| **@Valuation** | Financial modeling expert. Estimates valuation range using revenue multiples and comparable transactions. |
| **@Writer** | Investment memo specialist. Synthesizes all inputs into a VC/PE-grade memo with INVEST / PASS / MONITOR recommendation. |
| **@HumanReview** | Human-in-the-loop gate. The human reads the full memo and issues the final verdict. |

Each agent posts its output to the Band chat room using its own Agent API key and @mentions the next agent — the conversation is live and visible to everyone in the room.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Multi-agent coordination | [Band](https://band.ai) — Agent API |
| LLM | [Featherless AI](https://featherless.ai) — Qwen/Qwen2.5-72B-Instruct |
| Language | Python 3.10+ |
| Dependencies | `openai`, `requests`, `python-dotenv` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Band Chat Room                        │
│                                                              │
│  @Research → @Risk → @Valuation → @Writer → @HumanReview   │
│      ↑           ↑         ↑          ↑           ↑         │
│  Agent API   Agent API  Agent API  Agent API  Agent API     │
│    key         key        key        key        key         │
└─────────────────────────────────────────────────────────────┘
                              ↑
                    Featherless AI (Qwen2.5-72B)
                    OpenAI-compatible endpoint
```

Each agent is registered as a **Remote Agent** in Band and authenticates with its own `band_a_...` key. The @Research agent creates the chat room, adds all sibling agents and the human owner as participants, then kicks off the pipeline.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/dealdesk-ai
cd dealdesk-ai
```

### 2. Install dependencies

```bash
pip install python-dotenv openai requests
```

### 3. Register agents in Band

Go to [band.ai](https://band.ai) → **Remote Agents** → **Connect Remote Agent** and create 5 agents:

- `DealDesk Research`
- `DealDesk Risk`
- `DealDesk Valuation`
- `DealDesk Writer`
- `DealDesk HumanReview`

Save each agent's API key — **shown only once at creation**.

Update the UUIDs in `band_client.py` with your agent UUIDs.

### 4. Create `.env`

```bash
cp .env.example .env
```

Fill in your keys:

```env
FEATHERLESS_API_KEY=rc_your_key_here
BAND_RESEARCH_KEY=band_a_your_key
BAND_RISK_KEY=band_a_your_key
BAND_VALUATION_KEY=band_a_your_key
BAND_WRITER_KEY=band_a_your_key
BAND_HUMANREVIEW_KEY=band_a_your_key
```

### 5. Run

```bash
python main.py
```

Enter the company name and any context. Watch the agents appear in your Band chat room.

---

## Project Structure

```
dealdesk-ai/
├── main.py          # Orchestrator — runs the pipeline
├── agents.py        # The 5 agent functions + system prompts
├── band_client.py   # Band Agent API client (chat, participants, messages)
├── llm.py           # Featherless AI / OpenAI-compatible LLM wrapper
├── config.py        # Loads credentials from .env
├── .env.example     # Template for environment variables
└── requirements.txt
```

---

## Output

At the end of each run, DealDesk AI saves a JSON report:

```json
{
  "company": "Stripe",
  "timestamp": "20260617_143022",
  "band_chat_id": "c41dce8d-...",
  "band_chat_url": "https://app.band.ai/chats/c41dce8d-...",
  "investment_memo": "# Stripe — Investment Memo\n...",
  "human_verdict": "✅ APPROVED — Memo approved. Forwarding to deal team.",
  "agent_transcript": [...]
}
```

---

## Why Band?

Band's Agent API lets multiple independent agents share a single chat room and communicate via @mentions — without any message broker, queue, or orchestration server. The entire multi-agent coordination happens through the chat interface, making the pipeline **transparent, auditable, and human-readable** by default.

---

## Hackathon

Built for the **Band of Agents Hackathon** on lablab.ai (June 2026).

**Team:** Jhon Tejada

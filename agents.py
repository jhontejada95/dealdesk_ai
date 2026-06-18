"""
DealDesk AI — The 5 agents
Each agent runs its analysis and posts results to the Band room via the log callback.
"""

from llm import call_llm


# ─── AGENT 1: RESEARCH ───────────────────────────────────────────────────────

RESEARCH_SYSTEM = """You are @Research, a senior investment analyst.
Analyze the target company and produce a structured brief covering:
1. Company overview (business model, product, market)
2. Key financials if available (revenue, growth, burn rate)
3. Founding team background
4. Competitive landscape (top 3 competitors)
5. Recent news and market signals

Be factual, concise, and flag data gaps clearly. Output in markdown."""


def agent_research(company: str, context: str, log) -> str:
    print(f"\n🔍 @Research analyzing {company}...")
    result = call_llm(RESEARCH_SYSTEM, f"Company: {company}\n\nContext:\n{context}")
    log("@Research", result, mention_next="@Risk")
    return result


# ─── AGENT 2: RISK ───────────────────────────────────────────────────────────

RISK_SYSTEM = """You are @Risk, a due diligence specialist.
Given a research brief, identify:
1. Business risks (market, competition, model sustainability)
2. Team risks (gaps, key-person dependency)
3. Financial risks (burn, runway, revenue concentration)
4. Legal/regulatory risks
5. Overall risk score: LOW / MEDIUM / HIGH with justification

Be critical. Output in markdown."""


def agent_risk(research: str, log) -> str:
    print("\n⚠️  @Risk evaluating red flags...")
    result = call_llm(RISK_SYSTEM, f"Research brief:\n\n{research}")
    log("@Risk", result, mention_next="@Valuation")
    return result


# ─── AGENT 3: VALUATION ──────────────────────────────────────────────────────

VALUATION_SYSTEM = """You are @Valuation, a financial modeling expert.
Given a research brief and risk assessment, estimate valuation using:
1. Revenue multiples (if revenue known)
2. Comparable transactions in the sector
3. Stage-based benchmarks (pre-seed → Series B)
4. Discount for HIGH risk companies

Provide:
- Estimated valuation range (low / mid / high)
- Key value drivers
- Key value destroyers
- Recommended entry terms

Output in markdown."""


def agent_valuation(research: str, risk: str, log) -> str:
    print("\n💰 @Valuation building model...")
    prompt = f"Research:\n{research}\n\nRisk assessment:\n{risk}"
    result = call_llm(VALUATION_SYSTEM, prompt)
    log("@Valuation", result, mention_next="@Writer")
    return result


# ─── AGENT 4: WRITER ─────────────────────────────────────────────────────────

WRITER_SYSTEM = """You are @Writer, an expert at investment memos.
Synthesize all inputs into a professional investment memo:

# [Company] — Investment Memo

## Executive Summary
## Company Overview
## Market Opportunity
## Competitive Position
## Risk Assessment
## Valuation
## Recommendation: INVEST / PASS / MONITOR
## Next Steps

Professional tone, suitable for a VC/PE investment committee. Output in markdown."""


def agent_writer(company: str, research: str, risk: str, valuation: str, log) -> str:
    print("\n📝 @Writer drafting investment memo...")
    prompt = (
        f"Company: {company}\n\n"
        f"Research:\n{research}\n\n"
        f"Risk:\n{risk}\n\n"
        f"Valuation:\n{valuation}"
    )
    result = call_llm(WRITER_SYSTEM, prompt, max_tokens=2048)
    log("@Writer", result, mention_next="@HumanReview")
    return result


# ─── AGENT 5: HUMAN REVIEW ───────────────────────────────────────────────────

def agent_human_review(memo: str, log) -> str:
    """Human-in-the-loop gate before the workflow completes."""
    print("\n" + "=" * 60)
    print("👤 @HumanReview — Memo ready for your approval")
    print("=" * 60)
    print(memo)
    print("=" * 60)
    print("\n[A] Approve  [R] Reject  [M] Request changes")

    decision = input("Your decision: ").strip().upper()

    if decision == "A":
        verdict = "✅ APPROVED — Memo approved. Forwarding to deal team."
    elif decision == "R":
        reason = input("Reason for rejection: ").strip()
        verdict = f"❌ REJECTED — {reason}"
    elif decision == "M":
        changes = input("Changes needed: ").strip()
        verdict = f"🔄 CHANGES REQUESTED — {changes}"
    else:
        verd
"""
DealDesk AI — Web Dashboard
Run: python dashboard.py
Open: http://localhost:5000
"""

import json
import queue
import threading
import sys
import os

from flask import Flask, render_template_string, request, Response, jsonify

sys.path.insert(0, os.path.dirname(__file__))
from band_client import create_chat, send_message, verify_connection
from agents import agent_research, agent_risk, agent_valuation, agent_writer

app = Flask(__name__)
_queue = None
_band_chat_id = None

# ── HTML template (single-file) ───────────────────────────────────────────────
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>DealDesk AI — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{
  --navy:#0A0F1E; --navy2:#0F1628; --navy3:#151d35;
  --gold:#C9A84C; --gold2:#e8c46a;
  --blue:#2563EB; --blue2:#3b82f6;
  --text:#F0F4FF; --muted:#8A9BC0;
  --green:#10B981; --red:#EF4444;
  --border:rgba(201,168,76,0.2);
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--navy);color:var(--text);font-family:'Inter',-apple-system,sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden;}

/* HEADER */
header{
  display:flex;align-items:center;justify-content:space-between;
  padding:.85rem 1.5rem;
  background:var(--navy2);border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.logo{font-size:1.1rem;font-weight:800;color:var(--gold);}
.logo span{color:var(--blue2);}
#band-link{font-size:.8rem;color:var(--muted);text-decoration:none;}
#band-link:hover{color:var(--text);}
#status-bar{font-size:.78rem;color:var(--muted);display:flex;align-items:center;gap:.5rem;}
.dot{width:8px;height:8px;border-radius:50%;background:var(--green);}

/* LAYOUT */
.layout{display:grid;grid-template-columns:320px 1fr;flex:1;overflow:hidden;}

/* LEFT PANEL */
.left{
  background:var(--navy2);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow-y:auto;
}
.panel-section{padding:1.25rem;border-bottom:1px solid var(--border);}
.panel-label{font-size:.7rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:1px;margin-bottom:.75rem;}
input,textarea{
  width:100%;background:var(--navy3);border:1px solid var(--border);
  color:var(--text);border-radius:8px;padding:.65rem .85rem;
  font-size:.88rem;font-family:inherit;resize:none;
  transition:border-color .2s;
}
input:focus,textarea:focus{outline:none;border-color:var(--gold);}
textarea{height:90px;margin-top:.6rem;}
label{font-size:.78rem;color:var(--muted);display:block;margin-bottom:.35rem;}
.btn-run{
  width:100%;margin-top:.85rem;padding:.75rem;
  background:var(--gold);color:var(--navy);
  font-weight:700;font-size:.9rem;border:none;
  border-radius:8px;cursor:pointer;transition:opacity .2s;
}
.btn-run:hover{opacity:.9;}
.btn-run:disabled{opacity:.4;cursor:not-allowed;}

/* PIPELINE STEPS */
.pipeline{display:flex;flex-direction:column;gap:.5rem;}
.step{
  display:flex;align-items:center;gap:.75rem;
  padding:.65rem .85rem;border-radius:8px;
  border:1px solid transparent;
  transition:all .3s;
}
.step.waiting{color:var(--muted);}
.step.running{border-color:var(--gold);background:rgba(201,168,76,.07);color:var(--text);}
.step.done{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.05);color:var(--green);}
.step-icon{font-size:1.1rem;width:24px;text-align:center;flex-shrink:0;}
.step-name{font-size:.85rem;font-weight:600;}
.step-status{margin-left:auto;font-size:.7rem;}
.spinner{display:inline-block;width:10px;height:10px;border:2px solid var(--gold);border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}

/* RIGHT PANEL */
.right{display:flex;flex-direction:column;overflow:hidden;}
.feed{flex:1;overflow-y:auto;padding:1.25rem;display:flex;flex-direction:column;gap:1rem;}
.agent-msg{
  background:var(--navy2);border:1px solid var(--border);
  border-radius:10px;padding:1rem 1.25rem;animation:fadeIn .3s ease;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.msg-header{display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;}
.msg-agent{font-size:.8rem;font-weight:700;}
.msg-agent.research{color:#60a5fa;}
.msg-agent.risk{color:#f87171;}
.msg-agent.valuation{color:#34d399;}
.msg-agent.writer{color:#a78bfa;}
.msg-agent.humanreview{color:var(--gold);}
.msg-time{font-size:.7rem;color:var(--muted);margin-left:auto;}
.msg-body{font-size:.85rem;color:var(--muted);line-height:1.7;}
.msg-body h1,.msg-body h2,.msg-body h3{color:var(--text);margin:.75rem 0 .35rem;}
.msg-body h1{font-size:1.1rem;}
.msg-body h2{font-size:1rem;}
.msg-body h3{font-size:.9rem;color:var(--gold);}
.msg-body p{margin-bottom:.5rem;}
.msg-body ul,.msg-body ol{padding-left:1.25rem;margin-bottom:.5rem;}
.msg-body li{margin-bottom:.2rem;}
.msg-body strong{color:var(--text);}
.msg-body code{background:rgba(37,99,235,.15);color:var(--blue2);padding:.1rem .35rem;border-radius:4px;font-size:.8em;}

/* HUMAN REVIEW */
.review-bar{
  padding:1rem 1.5rem;background:var(--navy2);
  border-top:1px solid var(--border);
  display:none;align-items:center;gap:1rem;flex-shrink:0;
}
.review-bar.visible{display:flex;}
.review-label{font-size:.85rem;color:var(--text);font-weight:600;margin-right:.5rem;}
.btn-approve{
  background:var(--green);color:#fff;font-weight:700;
  border:none;padding:.6rem 1.5rem;border-radius:8px;cursor:pointer;font-size:.85rem;
}
.btn-reject{
  background:var(--red);color:#fff;font-weight:700;
  border:none;padding:.6rem 1.5rem;border-radius:8px;cursor:pointer;font-size:.85rem;
}
.btn-changes{
  background:transparent;color:var(--muted);font-weight:600;
  border:1px solid var(--border);padding:.6rem 1.5rem;border-radius:8px;cursor:pointer;font-size:.85rem;
}
.verdict-badge{
  padding:.5rem 1.25rem;border-radius:8px;font-weight:700;font-size:.85rem;
}
.verdict-badge.approved{background:rgba(16,185,129,.15);color:var(--green);border:1px solid rgba(16,185,129,.3);}
.verdict-badge.rejected{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.3);}

/* EMPTY STATE */
.empty{
  flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  color:var(--muted);text-align:center;padding:2rem;gap:.75rem;
}
.empty-icon{font-size:3rem;opacity:.4;}
.empty p{font-size:.9rem;max-width:320px;line-height:1.6;}
</style>
</head>
<body>

<header>
  <div class="logo">DealDesk <span>AI</span></div>
  <div id="status-bar"><div class="dot"></div><span>Band connected</span></div>
  <a id="band-link" href="#" target="_blank">Open in Band ↗</a>
</header>

<div class="layout">

  <!-- LEFT -->
  <div class="left">
    <div class="panel-section">
      <div class="panel-label">Target Company</div>
      <label>Company name</label>
      <input type="text" id="company" placeholder="e.g. Stripe, Notion, Linear..." />
      <label>Context (optional)</label>
      <textarea id="context" placeholder="Funding stage, sector, recent news, valuation..."></textarea>
      <button class="btn-run" id="btn-run" onclick="startRun()">▶ Run Analysis</button>
    </div>

    <div class="panel-section">
      <div class="panel-label">Pipeline</div>
      <div class="pipeline">
        <div class="step waiting" id="step-research">
          <span class="step-icon">🔍</span>
          <span class="step-name">@Research</span>
          <span class="step-status" id="s-research">—</span>
        </div>
        <div class="step waiting" id="step-risk">
          <span class="step-icon">⚠️</span>
          <span class="step-name">@Risk</span>
          <span class="step-status" id="s-risk">—</span>
        </div>
        <div class="step waiting" id="step-valuation">
          <span class="step-icon">💰</span>
          <span class="step-name">@Valuation</span>
          <span class="step-status" id="s-valuation">—</span>
        </div>
        <div class="step waiting" id="step-writer">
          <span class="step-icon">📝</span>
          <span class="step-name">@Writer</span>
          <span class="step-status" id="s-writer">—</span>
        </div>
        <div class="step waiting" id="step-humanreview">
          <span class="step-icon">👤</span>
          <span class="step-name">@HumanReview</span>
          <span class="step-status" id="s-humanreview">—</span>
        </div>
      </div>
    </div>
  </div>

  <!-- RIGHT -->
  <div class="right">
    <div class="feed" id="feed">
      <div class="empty" id="empty-state">
        <div class="empty-icon">🏦</div>
        <p>Enter a company name and click <strong>Run Analysis</strong> to start the 5-agent pipeline.</p>
        <p style="font-size:.8rem;margin-top:.5rem;">Agents will coordinate through Band in real time.</p>
      </div>
    </div>
    <div class="review-bar" id="review-bar">
      <span class="review-label">👤 Human Decision Required:</span>
      <button class="btn-approve" onclick="sendVerdict('APPROVED')">✅ Approve</button>
      <button class="btn-reject" onclick="sendVerdict('REJECTED')">❌ Reject</button>
      <button class="btn-changes" onclick="sendVerdict('CHANGES')">🔄 Request Changes</button>
    </div>
  </div>
</div>

<script>
const AGENT_CLASS = {
  '@Research':'research','@Risk':'risk',
  '@Valuation':'valuation','@Writer':'writer','@HumanReview':'humanreview'
};
const STEP_MAP = {
  '@Research':'research','@Risk':'risk',
  '@Valuation':'valuation','@Writer':'writer','@HumanReview':'humanreview'
};

let es = null;

function now(){
  return new Date().toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
}

function setStep(agent, state){
  const key = STEP_MAP[agent];
  if(!key) return;
  const el = document.getElementById('step-'+key);
  const st = document.getElementById('s-'+key);
  el.className = 'step '+state;
  if(state==='running') st.innerHTML = '<div class="spinner"></div>';
  else if(state==='done') st.textContent = '✓';
  else st.textContent = '—';
}

function addMsg(agent, content){
  const feed = document.getElementById('feed');
  const empty = document.getElementById('empty-state');
  if(empty) empty.remove();

  const cls = AGENT_CLASS[agent] || 'research';
  const isWriter = agent === '@Writer';
  const rendered = isWriter ? marked.parse(content) : content.replace(/\\n/g,'<br>');

  const el = document.createElement('div');
  el.className = 'agent-msg';
  el.innerHTML = `
    <div class="msg-header">
      <span class="msg-agent ${cls}">${agent}</span>
      <span class="msg-time">${now()}</span>
    </div>
    <div class="msg-body">${rendered}</div>
  `;
  feed.appendChild(el);
  feed.scrollTop = feed.scrollHeight;
}

async function startRun(){
  const company = document.getElementById('company').value.trim();
  const context = document.getElementById('context').value.trim();
  if(!company){ alert('Enter a company name.'); return; }

  document.getElementById('btn-run').disabled = true;
  document.getElementById('review-bar').classList.remove('visible');

  // Reset steps
  ['research','risk','valuation','writer','humanreview'].forEach(k=>{
    document.getElementById('step-'+k).className='step waiting';
    document.getElementById('s-'+k).textContent='—';
  });

  // Clear feed
  document.getElementById('feed').innerHTML = '';

  // Start run
  await fetch('/api/run', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({company, context})
  });

  // Stream events
  if(es) es.close();
  es = new EventSource('/api/stream');

  es.onmessage = function(e){
    const data = JSON.parse(e.data);

    if(data.type === 'status'){
      if(data.chat_id){
        const link = document.getElementById('band-link');
        link.href = `https://app.band.ai/chats/${data.chat_id}`;
        link.textContent = `Open in Band: ${data.chat_id.slice(0,8)}… ↗`;
      }
    }

    if(data.type === 'step'){
      setStep(data.agent, data.status);
    }

    if(data.type === 'agent'){
      addMsg(data.agent, data.content);
    }

    if(data.type === 'memo'){
      setStep('@HumanReview', 'running');
      document.getElementById('s-humanreview').innerHTML = '<div class="spinner"></div>';
      document.getElementById('review-bar').classList.add('visible');
    }

    if(data.type === 'done'){
      es.close();
      document.getElementById('btn-run').disabled = false;
    }
  };

  es.onerror = function(){
    es.close();
    document.getElementById('btn-run').disabled = false;
  };
}

async function sendVerdict(v){
  const bar = document.getElementById('review-bar');
  bar.innerHTML = `<span class="verdict-badge ${v==='APPROVED'?'approved':'rejected'}">${
    v==='APPROVED'?'✅ APPROVED — Memo forwarded to deal team':
    v==='REJECTED'?'❌ REJECTED':'🔄 Changes Requested'
  }</span>`;

  await fetch('/api/verdict', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({verdict: v})
  });

  setStep('@HumanReview','done');
  addMsg('@HumanReview', v==='APPROVED'
    ? '✅ **APPROVED** — Investment memo approved. Forwarding to deal team.'
    : v==='REJECTED'
    ? '❌ **REJECTED** — Deal rejected.'
    : '🔄 **CHANGES REQUESTED** — Memo sent back for revision.'
  );
  document.getElementById('btn-run').disabled = false;
}
</script>
</body>
</html>"""

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(TEMPLATE)


@app.route("/api/run", methods=["POST"])
def run_analysis():
    global _queue, _band_chat_id
    data = request.json
    company = data.get("company", "").strip()
    context = data.get("context", "").strip() or "No additional context."

    _queue = queue.Queue()
    q = _queue

    def pipeline():
        try:
            band_online = verify_connection()
            chat_id = create_chat(f"DealDesk AI — {company} Due Diligence")
            global _band_chat_id
            _band_chat_id = chat_id
            q.put({"type": "status", "chat_id": chat_id})

            def log(agent, content, mention_next=None):
                q.put({"type": "agent", "agent": agent, "content": content})
                if band_online and not chat_id.startswith("local-"):
                    send_message(chat_id, agent, content, mention_next)

            # Kickoff
            log("@Research", f"🚀 DealDesk AI — Target: **{company}**\nStarting pipeline…", "@Risk")

            q.put({"type": "step", "agent": "@Research", "status": "running"})
            research = agent_research(company, context, log)
            q.put({"type": "step", "agent": "@Research", "status": "done"})

            q.put({"type": "step", "agent": "@Risk", "status": "running"})
            risk = agent_risk(research, log)
            q.put({"type": "step", "agent": "@Risk", "status": "done"})

            q.put({"type": "step", "agent": "@Valuation", "status": "running"})
            valuation = agent_valuation(research, risk, log)
            q.put({"type": "step", "agent": "@Valuation", "status": "done"})

            q.put({"type": "step", "agent": "@Writer", "status": "running"})
            memo = agent_writer(company, research, risk, valuation, log)
            q.put({"type": "step", "agent": "@Writer", "status": "done"})

            q.put({"type": "memo", "content": memo, "chat_id": chat_id})

        except Exception as e:
            q.put({"type": "error", "msg": str(e)})
        finally:
            q.put(None)

    threading.Thread(target=pipeline, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/stream")
def stream():
    q = _queue

    def generate():
        while True:
            try:
                item = q.get(timeout=180)
                if item is None:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/verdict", methods=["POST"])
def verdict():
    data = request.json
    return jsonify({"status": "ok", "verdict": data.get("verdict", "PENDING")})


if __name__ == "__main__":
    print("\n🏦 DealDesk AI Dashboard")
    print("   http://localhost:5000\n")
    app.run(debug=False, port=5000, threaded=True)

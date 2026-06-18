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
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{
  --navy:#03070f;
  --navy2:#080d1a;
  --gold:#C9A84C;
  --gold2:#e8c46a;
  --blue:#2563EB;
  --blue2:#3b82f6;
  --text:#F0F4FF;
  --muted:#6b7fa3;
  --green:#10B981;
  --red:#EF4444;
  --amber:#F59E0B;
  --glass:rgba(255,255,255,0.04);
  --glass-border:rgba(255,255,255,0.08);
  --gold-border:rgba(201,168,76,0.25);
}
*{margin:0;padding:0;box-sizing:border-box;}
body{
  background:var(--navy);
  color:var(--text);
  font-family:'Inter',-apple-system,sans-serif;
  display:flex;
  flex-direction:column;
  height:100vh;
  overflow:hidden;
  position:relative;
}

/* ── BACKGROUND ORBS ─────────────────────────────────── */
.orb{
  position:fixed;border-radius:50%;pointer-events:none;z-index:0;
  filter:blur(100px);opacity:.55;
}
.orb1{width:600px;height:600px;top:-200px;left:-150px;
  background:radial-gradient(circle,rgba(201,168,76,.22) 0%,transparent 70%);
  animation:floatOrb 18s ease-in-out infinite;}
.orb2{width:500px;height:500px;bottom:-180px;right:-120px;
  background:radial-gradient(circle,rgba(37,99,235,.25) 0%,transparent 70%);
  animation:floatOrb 22s ease-in-out infinite reverse;}
.orb3{width:350px;height:350px;top:40%;right:30%;
  background:radial-gradient(circle,rgba(201,168,76,.1) 0%,transparent 70%);
  animation:floatOrb 26s ease-in-out infinite 4s;}
@keyframes floatOrb{
  0%,100%{transform:translate(0,0);}
  33%{transform:translate(30px,-20px);}
  66%{transform:translate(-20px,25px);}
}

/* ── GRID OVERLAY ────────────────────────────────────── */
.grid-bg{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(201,168,76,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(201,168,76,.025) 1px,transparent 1px);
  background-size:48px 48px;
}

/* ── HEADER ─────────────────────────────────────────── */
header{
  position:relative;z-index:10;
  display:flex;align-items:center;gap:1.5rem;
  padding:.9rem 1.75rem;
  background:rgba(3,7,15,.7);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border-bottom:1px solid var(--glass-border);
  flex-shrink:0;
}
.logo{
  font-size:1.15rem;font-weight:800;letter-spacing:-.02em;
  background:linear-gradient(135deg,var(--gold),var(--gold2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.logo-ai{
  background:linear-gradient(135deg,var(--blue),var(--blue2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.header-tag{
  font-family:'Fira Code',monospace;font-size:.65rem;
  color:var(--muted);letter-spacing:.08em;
  background:var(--glass);border:1px solid var(--glass-border);
  padding:.2rem .6rem;border-radius:4px;
}
.header-right{display:flex;align-items:center;gap:1.25rem;margin-left:auto;}
#status-bar{
  display:flex;align-items:center;gap:.5rem;
  font-size:.75rem;color:var(--muted);
}
.status-dot{
  width:7px;height:7px;border-radius:50%;
  background:var(--green);
  box-shadow:0 0 6px var(--green);
  animation:pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.4}}
#band-link{
  font-size:.75rem;color:var(--muted);text-decoration:none;
  font-family:'Fira Code',monospace;
  transition:color .2s;
}
#band-link:hover{color:var(--gold);}

/* ── LAYOUT ─────────────────────────────────────────── */
.layout{
  position:relative;z-index:5;
  display:grid;grid-template-columns:310px 1fr;
  flex:1;overflow:hidden;
}

/* ── LEFT PANEL ─────────────────────────────────────── */
.left{
  background:rgba(8,13,26,.6);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-right:1px solid var(--glass-border);
  display:flex;flex-direction:column;overflow-y:auto;
}
.left::-webkit-scrollbar{width:3px;}
.left::-webkit-scrollbar-thumb{background:var(--gold-border);border-radius:2px;}
.panel-section{padding:1.25rem 1.5rem;border-bottom:1px solid rgba(255,255,255,.05);}
.panel-label{
  font-size:.65rem;font-weight:700;color:var(--gold);
  text-transform:uppercase;letter-spacing:.12em;
  margin-bottom:.9rem;display:flex;align-items:center;gap:.5rem;
}
.panel-label::after{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--gold-border),transparent);
}
label{font-size:.75rem;color:var(--muted);display:block;margin-bottom:.4rem;}
input,textarea{
  width:100%;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08);
  color:var(--text);border-radius:10px;
  padding:.7rem .95rem;
  font-size:.85rem;font-family:inherit;resize:none;
  transition:border-color .25s,background .25s;
}
input::placeholder,textarea::placeholder{color:rgba(107,127,163,.6);}
input:focus,textarea:focus{
  outline:none;
  border-color:var(--gold);
  background:rgba(201,168,76,.05);
}
textarea{height:95px;margin-top:.6rem;}

.btn-run{
  width:100%;margin-top:1rem;padding:.8rem;
  background:linear-gradient(135deg,var(--gold),#b8932e);
  color:#03070f;
  font-weight:700;font-size:.875rem;
  border:none;border-radius:10px;cursor:pointer;
  letter-spacing:.03em;
  box-shadow:0 4px 20px rgba(201,168,76,.25);
  transition:all .25s;
  position:relative;overflow:hidden;
}
.btn-run::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.15),transparent);
  opacity:0;transition:opacity .25s;
}
.btn-run:hover:not(:disabled)::after{opacity:1;}
.btn-run:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 6px 28px rgba(201,168,76,.35);}
.btn-run:disabled{opacity:.35;cursor:not-allowed;transform:none;}

/* ── PIPELINE STEPS ─────────────────────────────────── */
.pipeline{display:flex;flex-direction:column;gap:.4rem;}
.step{
  display:flex;align-items:center;gap:.8rem;
  padding:.65rem .9rem;border-radius:10px;
  border:1px solid transparent;
  transition:all .35s cubic-bezier(.4,0,.2,1);
  cursor:default;
}
.step.waiting{
  color:var(--muted);
  background:transparent;
}
.step.running{
  border-color:var(--gold-border);
  background:rgba(201,168,76,.08);
  color:var(--text);
  box-shadow:0 0 20px rgba(201,168,76,.08);
}
.step.done{
  border-color:rgba(16,185,129,.25);
  background:rgba(16,185,129,.06);
  color:var(--green);
}
.step-icon{font-size:1rem;width:22px;text-align:center;flex-shrink:0;}
.step-name{font-size:.82rem;font-weight:600;font-family:'Inter',sans-serif;}
.step-status{margin-left:auto;font-size:.7rem;font-family:'Fira Code',monospace;}
.spinner{
  display:inline-block;width:11px;height:11px;
  border:2px solid rgba(201,168,76,.3);
  border-top-color:var(--gold);
  border-radius:50%;
  animation:spin .75s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── RIGHT PANEL ─────────────────────────────────────── */
.right{display:flex;flex-direction:column;overflow:hidden;background:transparent;}

.feed{
  flex:1;overflow-y:auto;
  padding:1.5rem;
  display:flex;flex-direction:column;gap:1rem;
}
.feed::-webkit-scrollbar{width:3px;}
.feed::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:2px;}

/* ── AGENT MESSAGE CARDS ─────────────────────────────── */
.agent-msg{
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.07);
  border-radius:14px;
  padding:1.1rem 1.35rem;
  backdrop-filter:blur(8px);
  animation:fadeSlide .35s cubic-bezier(.4,0,.2,1);
  transition:border-color .2s;
}
.agent-msg:hover{border-color:rgba(255,255,255,.12);}
@keyframes fadeSlide{
  from{opacity:0;transform:translateY(10px)}
  to{opacity:1;transform:none}
}

/* colored left border per agent */
.agent-msg.research{border-left:3px solid #60a5fa;}
.agent-msg.risk{border-left:3px solid #f87171;}
.agent-msg.valuation{border-left:3px solid #34d399;}
.agent-msg.writer{border-left:3px solid #a78bfa;}
.agent-msg.humanreview{border-left:3px solid var(--gold);}

.msg-header{display:flex;align-items:center;gap:.65rem;margin-bottom:.7rem;}
.agent-avatar{
  width:26px;height:26px;border-radius:7px;
  display:flex;align-items:center;justify-content:center;
  font-size:.8rem;flex-shrink:0;font-weight:700;
  font-family:'Fira Code',monospace;
}
.avatar-research{background:rgba(96,165,250,.15);color:#60a5fa;}
.avatar-risk{background:rgba(248,113,113,.15);color:#f87171;}
.avatar-valuation{background:rgba(52,211,153,.15);color:#34d399;}
.avatar-writer{background:rgba(167,139,250,.15);color:#a78bfa;}
.avatar-humanreview{background:rgba(201,168,76,.15);color:var(--gold);}

.msg-agent{font-size:.78rem;font-weight:700;font-family:'Fira Code',monospace;}
.msg-agent.research{color:#60a5fa;}
.msg-agent.risk{color:#f87171;}
.msg-agent.valuation{color:#34d399;}
.msg-agent.writer{color:#a78bfa;}
.msg-agent.humanreview{color:var(--gold);}
.msg-time{font-size:.68rem;color:var(--muted);margin-left:auto;font-family:'Fira Code',monospace;}
.msg-body{font-size:.84rem;color:rgba(240,244,255,.75);line-height:1.75;}
.msg-body h1,.msg-body h2,.msg-body h3{color:var(--text);margin:.8rem 0 .4rem;}
.msg-body h1{font-size:1.05rem;color:var(--text);}
.msg-body h2{font-size:.95rem;color:var(--text);}
.msg-body h3{font-size:.88rem;color:var(--gold);}
.msg-body p{margin-bottom:.5rem;}
.msg-body ul,.msg-body ol{padding-left:1.35rem;margin-bottom:.5rem;}
.msg-body li{margin-bottom:.25rem;}
.msg-body strong{color:var(--text);}
.msg-body em{color:var(--muted);}
.msg-body code{
  background:rgba(37,99,235,.15);color:#93c5fd;
  padding:.15rem .4rem;border-radius:5px;
  font-size:.78em;font-family:'Fira Code',monospace;
}
.msg-body blockquote{
  border-left:2px solid var(--gold-border);
  padding-left:.85rem;color:var(--muted);
  margin:.5rem 0;
}
.msg-body hr{border:none;border-top:1px solid rgba(255,255,255,.06);margin:.75rem 0;}

/* ── HUMAN REVIEW BAR ───────────────────────────────── */
.review-bar{
  position:relative;z-index:10;
  padding:1rem 1.75rem;
  background:rgba(3,7,15,.85);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border-top:1px solid var(--gold-border);
  display:none;align-items:center;gap:.85rem;flex-shrink:0;
  box-shadow:0 -8px 40px rgba(201,168,76,.08);
}
.review-bar.visible{display:flex;}
.review-label{
  font-size:.8rem;font-weight:600;color:var(--text);
  margin-right:.25rem;display:flex;align-items:center;gap:.5rem;
}
.review-label::before{
  content:'';display:inline-block;
  width:8px;height:8px;border-radius:50%;
  background:var(--gold);
  box-shadow:0 0 8px var(--gold);
  animation:pulse-dot 1.5s ease-in-out infinite;
}
.btn-approve{
  background:linear-gradient(135deg,#059669,#10B981);
  color:#fff;font-weight:700;
  border:none;padding:.6rem 1.35rem;border-radius:9px;
  cursor:pointer;font-size:.82rem;letter-spacing:.02em;
  box-shadow:0 3px 14px rgba(16,185,129,.3);
  transition:all .2s;
}
.btn-approve:hover{transform:translateY(-1px);box-shadow:0 5px 18px rgba(16,185,129,.4);}
.btn-reject{
  background:linear-gradient(135deg,#dc2626,#EF4444);
  color:#fff;font-weight:700;
  border:none;padding:.6rem 1.35rem;border-radius:9px;
  cursor:pointer;font-size:.82rem;letter-spacing:.02em;
  box-shadow:0 3px 14px rgba(239,68,68,.25);
  transition:all .2s;
}
.btn-reject:hover{transform:translateY(-1px);box-shadow:0 5px 18px rgba(239,68,68,.35);}
.btn-changes{
  background:var(--glass);color:var(--muted);font-weight:600;
  border:1px solid var(--glass-border);
  padding:.6rem 1.35rem;border-radius:9px;
  cursor:pointer;font-size:.82rem;
  transition:all .2s;
}
.btn-changes:hover{border-color:var(--gold-border);color:var(--text);}
.verdict-badge{
  padding:.55rem 1.25rem;border-radius:9px;
  font-weight:700;font-size:.82rem;
  font-family:'Fira Code',monospace;letter-spacing:.03em;
}
.verdict-badge.approved{
  background:rgba(16,185,129,.12);color:var(--green);
  border:1px solid rgba(16,185,129,.3);
  box-shadow:0 0 20px rgba(16,185,129,.1);
}
.verdict-badge.rejected{
  background:rgba(239,68,68,.12);color:var(--red);
  border:1px solid rgba(239,68,68,.3);
  box-shadow:0 0 20px rgba(239,68,68,.1);
}
.verdict-badge.changes{
  background:rgba(245,158,11,.1);color:var(--amber);
  border:1px solid rgba(245,158,11,.25);
}

/* ── EMPTY STATE ─────────────────────────────────────── */
.empty{
  flex:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  color:var(--muted);text-align:center;padding:3rem;gap:1rem;
}
.empty-icon{
  font-size:3.5rem;opacity:.25;
  filter:grayscale(1);
  margin-bottom:.5rem;
}
.empty h3{font-size:1rem;font-weight:600;color:rgba(240,244,255,.4);}
.empty p{font-size:.83rem;max-width:300px;line-height:1.65;color:rgba(107,127,163,.6);}
.empty-tag{
  font-family:'Fira Code',monospace;font-size:.7rem;
  color:var(--gold);opacity:.5;
  margin-top:.5rem;letter-spacing:.08em;
}
</style>
</head>
<body>

<!-- Background -->
<div class="grid-bg"></div>
<div class="orb orb1"></div>
<div class="orb orb2"></div>
<div class="orb orb3"></div>

<!-- Header -->
<header>
  <div class="logo">DealDesk <span class="logo-ai">AI</span></div>
  <div class="header-tag">M&amp;A Due Diligence · 5-Agent Pipeline</div>
  <div class="header-right">
    <div id="status-bar">
      <div class="status-dot"></div>
      <span>Band Live</span>
    </div>
    <a id="band-link" href="#" target="_blank">band://open ↗</a>
  </div>
</header>

<div class="layout">

  <!-- ── LEFT PANEL ───────────────────────────────────── -->
  <div class="left">

    <div class="panel-section">
      <div class="panel-label">Target</div>
      <label>Company name</label>
      <input type="text" id="company" placeholder="Stripe, Notion, Linear…" />
      <label style="margin-top:.75rem;">Context <span style="opacity:.5;">(optional)</span></label>
      <textarea id="context" placeholder="Funding stage, sector, valuation, recent news…"></textarea>
      <button class="btn-run" id="btn-run" onclick="startRun()">▶&nbsp;&nbsp;Run Analysis</button>
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

    <div class="panel-section" style="margin-top:auto;border-top:1px solid rgba(255,255,255,.04);border-bottom:none;">
      <div style="font-size:.68rem;color:var(--muted);line-height:1.8;font-family:'Fira Code',monospace;">
        <div style="color:var(--gold);margin-bottom:.4rem;letter-spacing:.08em;">TECH STACK</div>
        Featherless AI · Qwen2.5-72B<br/>
        Band Agent API · 5 agents<br/>
        Python · Flask · SSE
      </div>
    </div>

  </div>

  <!-- ── RIGHT PANEL ──────────────────────────────────── -->
  <div class="right">
    <div class="feed" id="feed">
      <div class="empty" id="empty-state">
        <div class="empty-icon">🏦</div>
        <h3>No analysis running</h3>
        <p>Enter a target company and click <strong>Run Analysis</strong> to deploy the 5-agent pipeline.</p>
        <div class="empty-tag">@Research → @Risk → @Valuation → @Writer → @HumanReview</div>
      </div>
    </div>

    <!-- Human Review Bar -->
    <div class="review-bar" id="review-bar">
      <span class="review-label">Human Decision Required</span>
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
const AGENT_ICON = {
  '@Research':'R','@Risk':'!','@Valuation':'$','@Writer':'W','@HumanReview':'H'
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
  const icon = AGENT_ICON[agent] || '?';
  const isWriter = agent === '@Writer';
  const rendered = isWriter ? marked.parse(content) : content.replace(/\\n/g,'<br>').replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');

  const el = document.createElement('div');
  el.className = 'agent-msg ' + cls;
  el.innerHTML = `
    <div class="msg-header">
      <div class="agent-avatar avatar-${cls}">${icon}</div>
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

  // Start pipeline
  await fetch('/api/run', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({company, context})
  });

  // Stream SSE events
  if(es) es.close();
  es = new EventSource('/api/stream');

  es.onmessage = function(e){
    const data = JSON.parse(e.data);

    if(data.type === 'status'){
      if(data.chat_id){
        const link = document.getElementById('band-link');
        link.href = `https://app.band.ai/chats/${data.chat_id}`;
        link.textContent = `band://${data.chat_id.slice(0,8)}… ↗`;
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
  const cls = v==='APPROVED'?'approved':v==='REJECTED'?'rejected':'changes';
  const label = v==='APPROVED'
    ? '✅ APPROVED — Forwarding to deal team'
    : v==='REJECTED'
    ? '❌ REJECTED — Deal closed'
    : '🔄 CHANGES REQUESTED';
  bar.innerHTML = `<span class="verdict-badge ${cls}">${label}</span>`;

  await fetch('/api/verdict', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({verdict: v})
  });

  setStep('@HumanReview','done');
  addMsg('@HumanReview',
    v==='APPROVED' ? '✅ **APPROVED** — Investment memo approved. Forwarding to deal team.'
    : v==='REJECTED' ? '❌ **REJECTED** — Deal rejected.'
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

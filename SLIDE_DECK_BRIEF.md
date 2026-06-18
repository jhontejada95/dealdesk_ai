# DealDesk AI — Slide Deck Brief para Claude Design

## Estilo visual

**Concepto:** Sala de guerra de M&A. Serio, profesional, con tensión de alto riesgo financiero.

**Paleta de colores:**
- Fondo principal: `#0A0F1E` (azul marino muy oscuro, casi negro)
- Acento primario: `#C9A84C` (oro financiero)
- Acento secundario: `#2563EB` (azul eléctrico para tecnología)
- Texto principal: `#F0F4FF` (blanco frío)
- Texto secundario: `#8A9BC0` (gris azulado)
- Verde aprobación: `#10B981`
- Rojo riesgo: `#EF4444`

**Tipografía:**
- Títulos: Sans-serif bold, geométrica (ej. Inter Bold o similar)
- Cuerpo: Sans-serif regular, limpia
- Código/datos: Monospace

**Elementos visuales:**
- Líneas finas en dorado para separadores
- Iconos minimalistas (outline style)
- Flechas conectando agentes (el pipeline)
- Sin fotos de stock, todo vectorial/tipográfico
- Sensación de terminal/dashboard financiero

---

## Slides — Contenido

### SLIDE 1 — Portada
**Título:** DealDesk AI
**Subtítulo:** 5 AI Agents · Real-Time M&A Due Diligence · Human in the Loop
**Visual:** Logo o ícono de edificio bancario / gráfico de red de agentes conectados
**Elemento inferior:** "Band of Agents Hackathon · June 2026"

---

### SLIDE 2 — El Problema
**Título:** Due diligence takes weeks. Deals move in days.

**Cuerpo (3 puntos):**
- Traditional M&A due diligence: 4–8 weeks, 5–15 analysts, $50K–$500K in fees
- By the time the memo is ready, the opportunity may be gone
- Junior analysts spend 80% of time gathering data, not thinking

**Visual:** Timeline con dos barras — "Traditional" (larga, roja) vs "DealDesk AI" (corta, verde)

---

### SLIDE 3 — La Solución
**Título:** 5 specialized AI agents. One chat room. One investment memo.

**Cuerpo:**
DealDesk AI deploys a team of AI agents that collaborate in real time through a Band chat room — each agent a specialist, each message an audit trail.

**Visual:** Diagrama de flujo horizontal:
`@Research → @Risk → @Valuation → @Writer → @HumanReview ✓`
Con íconos distintos para cada agente y una línea dorada conectándolos.

---

### SLIDE 4 — Cómo funciona (The Pipeline)
**Título:** How it works

**5 bloques (uno por agente), cada uno con:**

| Agente | Ícono | Lo que hace |
|---|---|---|
| @Research | 🔍 | Analyzes business model, team, market, financials |
| @Risk | ⚠️ | Scores risks: LOW / MEDIUM / HIGH |
| @Valuation | 💰 | Estimates valuation range & entry terms |
| @Writer | 📝 | Produces VC/PE-grade investment memo |
| @HumanReview | 👤 | Human reads, decides: APPROVE / REJECT / REVISE |

**Visual:** Los 5 bloques en columnas con flechas entre ellos. Último bloque (@HumanReview) tiene borde dorado — resalta que es humano.

---

### SLIDE 5 — Band como capa de coordinación
**Título:** Why Band? Multi-agent coordination through conversation.

**3 puntos:**
- Each agent authenticates with its own Agent API key (`band_a_...`)
- Agents @mention the next agent — no message broker, no queue, no orchestration server
- The entire pipeline is visible in the Band chat UI — transparent and auditable by design

**Visual:** Screenshot (o mockup) del chat de Band con los mensajes de los 5 agentes apareciendo en cadena. Si tienes el chat real de la demo, úsalo.

---

### SLIDE 6 — Tech Stack
**Título:** Built on best-in-class open infrastructure

**3 columnas:**

**Multi-Agent Layer**
Band · Agent API
`band_a_...` keys
Real-time chat coordination

**LLM**
Featherless AI
Qwen/Qwen2.5-72B-Instruct
OpenAI-compatible endpoint

**Language**
Python 3.10+
Minimal dependencies
Runs anywhere

**Visual:** Logos de Band y Featherless AI (si los tienes) o íconos representativos en las 3 columnas sobre fondo oscuro.

---

### SLIDE 7 — Demo
**Título:** Live demo

**Subtítulo:** Analyzing Stripe — from zero to investment memo in under 3 minutes

**Visual:** Captura de pantalla o GIF del terminal corriendo `python main.py` junto al chat de Band con los agentes apareciendo.

*(Esta slide acompaña la demo en vivo o el video)*

---

### SLIDE 8 — Output
**Título:** What you get

**Dos columnas:**

**In Band (live)**
- Real-time agent conversation
- Full audit trail
- Each agent identified
- Human approval gate

**As a file**
- JSON report with full transcript
- Investment memo (markdown)
- Human verdict recorded
- Band chat URL for reference

**Visual:** Mockup de un JSON o memo con formato elegante a la derecha, y el chat de Band a la izquierda.

---

### SLIDE 9 — Por qué gana / Diferenciadores
**Título:** What makes DealDesk AI different

**4 puntos con íconos:**

🔍 **Specialized agents, not one LLM** — each agent has a focused system prompt and a single job

💬 **Band as the brain** — coordination happens through conversation, not code

👤 **Human always in the loop** — no memo ships without human approval

⚡ **Minutes, not weeks** — from company name to investment memo in under 5 minutes

---

### SLIDE 10 — Cierre / CTA
**Título:** DealDesk AI

**Subtítulo:** The fastest path from target company to investment decision.

**Links:**
- GitHub: `github.com/yourusername/dealdesk-ai`
- Demo chat: `app.band.ai/chats/[id]`

**Créditos:** Built by Jhon Tejada · Band of Agents Hackathon · June 2026

**Visual:** Mismo estilo que la portada. Línea dorada fina en la parte inferior.

---

## Notas para Claude Design

- **Formato:** 16:9 (1920×1080 o 1280×720)
- **Total slides:** 10
- **Tono:** Serio pero moderno — no corporativo clásico, sino fintech/startup de alto nivel
- **Elemento recurrente:** La cadena de agentes `@Research → @Risk → @Valuation → @Writer → @HumanReview` debe aparecer al menos en slides 3, 4 y 7 con el mismo estilo visual para que sea reconocible
- **Slide más importante visualmente:** Slide 4 (el pipeline) — que sea el más elaborado
- **Evitar:** Fotografías de personas, fondos blancos, estilo PowerPoint corporativo genérico

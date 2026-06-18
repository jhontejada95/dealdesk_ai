# DealDesk AI — Guion del Demo Video
**Duración objetivo:** 2:30 – 3:00 minutos
**Resolución:** 1920×1080, pantalla completa
**Herramienta de grabación sugerida:** OBS Studio o Loom

---

## Preparación antes de grabar

- [ ] Terminal abierto en la carpeta `dealdesk-ai/`
- [ ] `.env` con las 5 keys configurado
- [ ] Pestaña de Band abierta en `app.band.ai` con el chat listo (o abrirla durante la demo)
- [ ] Empresa de prueba elegida: **"Stripe"** (reconocible, datos públicos)
- [ ] Contexto preparado para pegar: `Global payments infrastructure company. Founded 2010 by the Collison brothers. ~$70B valuation, processing $1T+ annually.`
- [ ] Fuente del terminal aumentada (mínimo 18pt) para que se lea bien en video

---

## SEGMENTO 1 — Hook (0:00 – 0:20)

**Pantalla:** Slide de portada o terminal en negro

**Lo que dices:**
> "M&A due diligence normally takes weeks, costs hundreds of thousands of dollars, and requires a team of analysts. DealDesk AI does it in minutes — with 5 AI agents that coordinate in real time through Band, each one a specialist, each one leaving a live audit trail you can watch unfold."

---

## SEGMENTO 2 — Mostrar la arquitectura (0:20 – 0:45)

**Pantalla:** Slide 4 del deck (el pipeline de los 5 agentes)

**Lo que dices:**
> "The system has five agents. Research goes first — it gathers everything about the target company: business model, financials, team, competitors. Then Risk evaluates the red flags and scores them LOW, MEDIUM, or HIGH. Valuation builds the financial model and estimates a range. Writer synthesizes all of it into a VC-grade investment memo. And finally, a human reviewer reads the memo and makes the final call — approve, reject, or request changes. No memo ships without a human decision."

**Tip:** Señala cada agente mientras lo nombras.

---

## SEGMENTO 3 — Correr el pipeline en vivo (0:45 – 2:00)

**Pantalla:** Terminal

**Lo que dices mientras escribes:**
> "Let me show you this live. I'm going to run the system right now against a real company — Stripe."

*Escribes en terminal:*
```
python main.py
```

**Cuando pide el nombre de la empresa:**
> "The target company is Stripe."

*Escribes:* `Stripe`

**Cuando pide contexto:**
> "I'll give it a bit of context to work with."

*Pegas:* `Global payments infrastructure company. Founded 2010 by the Collison brothers. ~$70B valuation, processing $1T+ annually.`

*Presionas Enter dos veces.*

**Mientras el sistema corre (llena el silencio):**
> "You can see the agents starting up. Research is now calling the LLM with a specialized system prompt — it knows it's an investment analyst, it knows what it's looking for."

*(Cuando aparece el output de Research)*
> "Research just finished. It's already posted its analysis to the Band chat room and @mentioned Risk to take over."

*(Cuando corre Risk)*
> "Risk is evaluating the findings — business model sustainability, regulatory exposure, key-person dependency on the Collison brothers."

*(Cuando corre Valuation)*
> "Valuation is now building the model — revenue multiples, comparable transactions, stage-based benchmarks."

*(Cuando corre Writer)*
> "And Writer is synthesizing everything into the final memo."

---

## SEGMENTO 4 — Mostrar Band en vivo (2:00 – 2:30)

**Pantalla:** Cambias a la pestaña de Band en el navegador — el chat room con los mensajes de los agentes

**Lo que dices:**
> "Here's the key part. Everything the agents just did — it's all here, in Band. Each agent posted its output under its own identity. You can see Research, Risk, Valuation, Writer, each one @mentioning the next. This isn't a black box — it's a conversation. Anyone on the deal team can follow along in real time, ask questions, and see exactly how the decision was reached."

*Scrolleas hacia arriba para mostrar los primeros mensajes, luego bajas al final.*

> "And here — the human review gate. The system stopped and waited for a human to read the full memo and make the call."

---

## SEGMENTO 5 — Cierre (2:30 – 3:00)

**Pantalla:** Vuelves al terminal mostrando el JSON guardado, o a la slide de cierre

**Lo que dices:**
> "The result is a complete JSON report with the investment memo, the full agent transcript, and a link back to the Band chat for the audit trail. From company name to investment decision — under three minutes."

> "DealDesk AI. Built on Band for the Band of Agents Hackathon. The fastest path from target company to investment decision."

---

## Notas de producción

**Cortes recomendados:**
- Si el pipeline tarda mucho en el video, puedes hacer un jump cut entre "Research running" y el output final — o grabar con una empresa más corta de analizar como "Notion" o "Linear".

**Audio:**
- Graba en un lugar silencioso, sin eco
- Si tienes micrófono externo, úsalo — el audio importa más que el video en este tipo de demos

**Subtítulos:**
- Considera agregar subtítulos automáticos (Capcut, DaVinci Resolve, o la función de Loom) — muchos jueces ven los videos sin sonido

**Música de fondo (opcional):**
- Algo instrumental, bajo volumen — estilo "corporate tech" o lo dejas sin música para que el foco esté en el terminal y Band

**Duración máxima:**
- lablab.ai normalmente pide videos de máximo 3 minutos. Si te pasas, corta el Segmento 2 (arquitectura) y reemplázalo con una mención rápida de 5 segundos.

---

## Checklist antes de subir el video

- [ ] Se escucha claramente lo que dices
- [ ] El texto del terminal se lee bien
- [ ] El chat de Band con los mensajes de los 5 agentes es visible
- [ ] Mencionaste "Band" explícitamente al menos 2 veces
- [ ] Mencionaste "human in the loop" al menos 1 vez
- [ ] El video dura máximo 3:00 minutos
- [ ] El archivo está en MP4, menos de 500MB

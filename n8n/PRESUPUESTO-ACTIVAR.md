# Presupuesto para que los sistemas n8n funcionen

**Fecha:** 2026-08-04  
**Alcance:** solo proyectos creados activos en `n8n/sistemas/`  
**Confidence:** ~55% en precios de mercado (varían por país / plan); alto en *qué falta* técnicamente.

Hoy todo está en **esqueleto + mock** (`sin_api: true`, nodos grises a `127.0.0.1:9999`).  
No “vende solo”: falta enchufar APIs, un runner Cursor/CLI y un n8n estable (no tunnel efímero).

---

## 1. Qué le falta a cada sistema

| Sistema | Ya tiene | Falta para funcionar de verdad |
|---------|----------|--------------------------------|
| **Marketing Audit** | Webhooks mock + brief | Places/Maps o scrap controlado · runner `marketing-audit` · Sheet/Notion log · PDF/informe al cliente · WhatsApp de entrega |
| **Presencia web locales** | Alta/deploy mock | Runner landings · **Vercel/Netlify** token · dominio · checklist GBP (manual o API) · Wasap CTA |
| **Bot WhatsApp pymes** | Router FAQ/citas mock | **Meta Cloud API** (WABA verificado) · plantillas aprobadas · FAQ JSON por cliente · agenda (Sheet/Cal.com) · handoff a humano |
| **Embudo comercial HTML** | Lead webhook | Destino real: **Sheet / Notion / CRM** · aviso Slack/email · landing publicada con el form apuntando al webhook |
| **Libros / KDP** | Brief mock | Runner `libros a entender` + `kdp_main` · PDF fuente · (opcional) cuenta KDP — publicar en Amazon sigue siendo semi-manual |
| **LinkedIn ghostwriter** | Brief/posts mock | Runner `generar_posts.py` · carpeta output · publicar: **manual** o Buffer/Late (API LinkedIn restringida) |
| **Creador de contenido** | Lote mock | Runner `creador_imagenes_main` · ffmpeg · API imágenes (o local) · opcional Kling |
| **Videos TikTok** | Guion/render/listo mock | Mismo runner video 9:16 · slideshow gratis o **Kling** pago · captions · publicar: **manual** primero (API TikTok = aprobación lenta) |
| **Capa clientes** | Carpetas | Sin n8n; falta proceso + 1 cliente que pague |

**Compartido (bloquea a todos):**
1. **n8n permanente** (cloud o VPS) — el tunnel Cloudflare se cae  
2. **Runner** que ejecute los `*_main.py` (VPS, GitHub Action, o webhook a un agente)  
3. **Secrets** en n8n (Meta, Vercel, Sheets, LLM, Kling…)  
4. Activar workflows + URLs HTTPS fijas  

---

## 2. Costos mensuales (operar)

Montos en **USD aprox.** · escenario **piloto 1–3 clientes / bajo volumen**.

### Infra base (obligatorio)

| Ítem | Opción barata | Opción cómoda | Notas |
|------|---------------|---------------|-------|
| n8n | **VPS self-host $6–15/mes** | n8n Cloud Starter **~€20–24/mes** (~$22–26) | Pro ~€50–60/mes si hay más ejecuciones |
| Dominio | $10–15/año | idem | webhook estable |
| SSL / proxy | Cloudflare free | idem | |
| Google Sheet / Notion | $0 | Notion Plus ~$10 | log leads / tickets |
| Email aviso (opcional) | $0 (Gmail) | Resend ~$0–20 | |

**Subtotal infra mínima:** ~**$10–40/mes**

### APIs por producto (cuando lo uses)

| API / servicio | Piloto / mes | Si escala | Para qué |
|----------------|--------------|-----------|----------|
| Meta WhatsApp Cloud | **$5–40** (sobre todo templates; respuestas en ventana servicio a menudo $0 hasta cambios Meta) | $50–300+ | Bot + seguimiento audit |
| Vercel | $0 Hobby · **$20 Pro** si hace falta | $20+ | Presencia / landings |
| LLM (OpenAI/Anthropic) | **$20–80** | $100–400 | copy, guiones, audits, posts |
| Google Places / Maps | **$0–50** (créditos free limitados) | $50–200 | Audits locales |
| Kling / video AI | **$0** (slideshow ffmpeg) · **$30–150** animado | $200+ | TikTok / contenido animado |
| Buffer / Late (LinkedIn) | $0 manual · **$15–30** | $30+ | publicar posts |
| Cursor / IDE | (ya lo pagás) | — | runners / prompts |

**Subtotal APIs piloto típico:** ~**$50–200/mes** (sin Kling) · **+$50–150** si querés video animado serio.

### Totales mensuales orientativos

| Escenario | USD / mes | Qué incluye |
|-----------|-----------|-------------|
| **A · Mínimo viable** | **~$40–80** | VPS n8n + Sheet + LLM chico + Wasap bajo + landings Hobby + video slideshow (sin Kling) |
| **B · Piloto serio** | **~$120–250** | n8n Cloud o VPS bueno + Meta + Vercel Pro + LLM + Places + algo de Kling |
| **C · Producción contenido** | **~$300–600+** | B + Kling/volumen + más mensajes Wasap + más ejecuciones n8n |

---

## 3. Costo one-shot (ponerlos a andar una vez)

No es “compra de software”, es **setup + verificación**:

| Trabajo | Esfuerzo | Si lo pagás afuera (ref.) |
|---------|----------|---------------------------|
| n8n estable + DNS + backups | 0.5–1 día | $150–400 |
| Credencial Meta WABA + plantillas | 1–3 días (espera Meta) | $200–600 |
| Enchufar 3 sistemas comerciales (Audit + Presencia + Wasap + Embudo) | 2–4 días | $600–1.500 |
| Runner CLI Cursorprime en VPS | 0.5–1 día | $150–400 |
| TikTok/KDP/LinkedIn en modo “genera + publicás a mano” | 1–2 días | $300–800 |
| Kling real + pipeline video | 1–2 días | $300–800 |

**One-shot piloto (A→B):** orden de **$1.000–3.000** si contratás; **casi $0 cash** si lo armás vos (solo mes de APIs).

---

## 4. Orden recomendado (plata → valor)

1. **Infra** n8n permanente + Sheet + runner CLI  
2. **Embudo + Audit + Presencia** (plata entra)  
3. **Wasap FAQ/citas** (upsell)  
4. **Contenido / TikTok slideshow** (sin Kling)  
5. Kling + publicar APIs (lujo / escala)

Cola (`n8n/cola/` Vértice, Cola pedidos…): **no presupuestar** hasta que el panel los pase a creados.

---

## 5. Resumen en una frase

Para que **funcionen de verdad** falta: **n8n fijo + runners Cursor + Meta/Vercel/Sheets/LLM** (y Kling solo si querés video animado).  
**Presupuesto piloto realista: ~$80–200/mes** + setup (vos o ~$1k–3k one-shot).

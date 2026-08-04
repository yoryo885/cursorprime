# El 80% — qué hace Cursor (yo) vs qué automatiza n8n

El ~20% que **no** automatizamos: precio, oferta, claims sensibles, cierre de venta, gasto de APIs, incidentes sin runbook.

El ~80% sí: draft, clasificar, disparar pipelines, reportes, healthchecks, FAQ, lots de contenido.

---

## 1. Marketing (Tráfico / Adquisición)

| Rutina | Yo (agente Cursor) en el chat | Automatizar 24/7 |
|--------|-------------------------------|------------------|
| **M-01** Brief semanal | Genero 5 hooks + 3 ángulos + elegir oferta | Dom: skill `hooks-redes` + n8n “TikTok · nuevo guion” / LinkedIn brief |
| **M-02** Publicar / outreach | Redacto captions, UTM, 10 DMs plantilla+dato | `captions-redes` → cola; Sheet + mensajes (Wasap/Meta cuando haya API) |
| **M-03** Lead entra | Clasifico intención audit/presencia/wasap | **Embudo · formulario** → Sheet → mensaje auto (n8n 02 + 09) |
| **M-04** Retro viernes | Resumen 5 líneas: qué trajo leads | n8n lee Sheet → markdown semanal al DG |

**Skills que ya cubren el draft:** `hooks-redes`, `captions-redes`, `thumbnail-social`, `copy-linkedin`, `guion-a-video`, `audit-marketing`, `landing-lanzamiento`.

---

## 2. Operaciones (Soporte / Ejecución)

| Rutina | Yo (agente Cursor) | Automatizar 24/7 |
|--------|--------------------|------------------|
| **O-01** Healthcheck | Reviso logs / arreglo fallos | Ping n8n + alertas (cron) |
| **O-02** Entregar job | Corro `*_main.py`, armo brief, QA | Webhook n8n → runner CLI (falta enchufar) |
| **O-03** API sin_api→live | Configuro nodos, docs, prueba `--limit` | Checklist; credenciales = humano |
| **O-04** Incidente | Leo error, propongo fix, parche | Reintentos + resumen IA del log |

**Pipelines listos (disparo manual hoy):** marketing-audit, creador-de-landings / presencia, wasap FAQ, KDP, LinkedIn `generar_posts.py`, creador de contenido, videos TikTok (slideshow).

---

## 3. Cómo se reparte el trabajo

```
Cliente / lead / “quiero un audit”
        │
        ▼
   n8n (webhook)     ← 24/7, sin que estés en el chat
        │
        ├─ Sheet / Wasap FAQ
        └─ Runner → python *_main.py
                    │
                    ▼
              Cursor agente (yo)  ← cuando hace falta juicio, copy, fix, QA
                    │
                    ▼
              Entregable (PDF, landing, pack posts, short)
```

- **n8n** = el sistema que no duerme (recibir, encolar, avisar, reintentar).  
- **Yo** = el cerebro bajo demanda (escribir, diseñar, depurar, mejorar prompts).  
- **Vos (DG)** = el 20%: sí/no, precio, prioridad.

---

## 4. Para automatizarlo de verdad (orden)

1. **Runner fijo** — VPS o job que ejecute `python3 …_main.py --slug X` cuando n8n llame.  
2. **Embudo live** — lead webhook → Sheet (quitar `sin_api`).  
3. **M-01/M-02 en cola** — un workflow semanal que me dispare (o deje briefs en carpeta) para hooks/captions.  
4. **Wasap FAQ** — Meta cuando haya WABA; hasta entonces respuestas mock + handoff manual.  
5. **Healthcheck** — cron O-01 → Telegram/email si n8n cae.

Sin el paso 1, yo automatizo **en la conversación**; n8n no puede “llamarme” solo todavía.

---

## 5. Qué pedirme hoy (sin infra nueva)

Ejemplos que ya son el 80% en chat:

- “Hooks para Audit piloto esta semana” → M-01  
- “Caption + CTA para este reel” → M-02  
- “Corré audit demo Clínica Sol” → O-02  
- “Pack LinkedIn marzo” → pipeline LinkedIn  
- “Short TikTok slideshow del tema X” → sistema 14 + contenido  
- “Resumen del scorecard” → M-04 / viernes DG  

Cuando digas **enchufar runner** o **activar Embudo live**, pasamos del chat al 24/7.


---

## Estado 2026-08-04

MVP LIVE encendido: ver `n8n/COMO-EMPEZAR.md` (runner + embudo + tiktok guion + audit enqueue).

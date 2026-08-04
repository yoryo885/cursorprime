# Cómo empezar — sistema LIVE (MVP)

El embudo ya **no es solo mock**: n8n → **runner** → archivo/job.

## Qué está andando ahora

| Pieza | Estado |
|-------|--------|
| Runner `http://127.0.0.1:8780` | LIVE |
| **Embudo · formulario landing** | Activo → guarda leads |
| **TikTok · nuevo guion** | Activo → escribe brief |
| **Auditoría · disparar informe** | Activo → encola brief/job |
| **Ops · healthcheck** | Activo cada 15 min |

## Arrancar (si se reinicia la máquina)

```bash
# 1) n8n
cd n8n && npm start

# 2) runner (otra terminal / tmux)
bash scripts/start-runner.sh

# 3) tunnel opcional para celular
bash scripts/tunnel.sh
```

## Probar

```bash
# Lead
curl -X POST http://127.0.0.1:5678/webhook/lead-landing \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","email":"ana@demo.com","mensaje":"Quiero un audit"}'

# Ver leads
curl -s http://127.0.0.1:8780/leads | python3 -m json.tool

# TikTok brief
curl -X POST http://127.0.0.1:5678/webhook/tiktok/guion \
  -H 'Content-Type: application/json' \
  -d '{"tema":"3 errores en Google","slug":"tt-demo"}'
```

Leads: `n8n/runner/data/leads.jsonl`  
Jobs: `n8n/runner/jobs/`

## Ciclo si no te gusta el borrador

1. Sistema genera borrador (brief / job).  
2. Me decís qué cambiar.  
3. Yo regenero.  
4. Vos aprobás → recién ahí va a cliente/publicación.

## Qué falta para “producción total”

- Dominio fijo (no tunnel efímero)  
- Meta Wasap / Vercel / Kling reales  
- Runner ejecutando `*_main.py` completo (hoy encola briefs + jobs listos)

## Telegram
Ver  — destino @yoryo321.


## Telegram
Destino **@yoryo321**. Ver `TELEGRAM.md`.

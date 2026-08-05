# 03 — Wasap FAQ (esqueleto)

Webhook POST estilo Meta Cloud API → detecta intención simple (faq / humano) → responde texto.

## TODOs al insertar

- [ ] Credencial Meta WhatsApp Cloud API
- [ ] Verificar `hub.challenge` (nodo Verify si hace falta)
- [ ] Mapa FAQ real del cliente (`clientes/{slug}/`)
- [ ] Handoff a humano (etiqueta / aviso)

No es un bot genérico: **solo FAQ + handoff** (patrón task-scoped del radar).

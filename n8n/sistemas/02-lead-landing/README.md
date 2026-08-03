# 02 — Lead de landing

Recibe POST JSON de una landing (nombre, email, mensaje, marca) → limpia → responde `{ ok: true, leadId }`.

## Body esperado

```json
{
  "nombre": "Ana",
  "email": "ana@mail.com",
  "mensaje": "Quiero info",
  "marca": "Vértice Pro",
  "origen": "landing"
}
```

## TODOs al insertar

- [ ] Conectar Google Sheets / Notion / CRM (nodo vacío marcado)
- [ ] Opcional: Slack/Discord notificación
- [ ] CORS si el form llama desde el browser

**Insertar:** Import → Activate → pegar URL webhook en el form de la landing.

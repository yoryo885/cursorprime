# 04 — Disparo audit

POST `{ "url": "https://negocio.com", "cliente": "slug" }` → valida → ack para encolar audit marketing.

## TODOs

- [ ] Llamar pipeline `marketing-audit` (HTTP a runner / cola)
- [ ] Guardar job en Sheet
- [ ] Aviso cuando el informe esté listo

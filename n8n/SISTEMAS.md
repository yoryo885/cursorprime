# Sistemas n8n — solo diseño (insertar después)

No hace falta login ahora. Acá guardamos **sistemas listos** (JSON) para importar cuando tengas n8n.cloud o VPS.

## Cómo insertarlos después (celular o PC)

1. Abrí tu n8n (cloud o self-host)
2. Menú **⋯** → **Import from File** (o Workflows → Import)
3. Elegí el `.json` de `sistemas/{id}/workflows/*.json`
4. Completá credenciales marcadas `TODO_CREDENCIAL`
5. **Activate** → copiá la URL del Webhook si aplica

## Catálogo de negocio (ranking 1–4) ✅

| # | ID | Sistema | Entrega al cliente |
|---|-----|---------|-------------------|
| 1 | `06-auditorias-locales` | Auditorías | Informe score + puerta a planes |
| 2 | `07-presencia-digital` | Presencia digital | Web + GBP (+ Wasap) |
| 3 | `08-cola-pedidos-wasap` | Cola pedidos | Tickets + estados + avisos |
| 4 | `09-wasap-task-faq-citas` | Wasap task | FAQ + citas + handoff |

## Utilitarios (plantillas cortas)

| ID | Sistema | Archivo |
|----|---------|---------|
| `01-ping` | Ping salud | `sistemas/01-ping/` |
| `02-lead-landing` | Lead landing | `sistemas/02-lead-landing/` |
| `03-wasap-faq` | FAQ corto | `sistemas/03-wasap-faq/` |
| `04-audit-trigger` | Disparo audit genérico | `sistemas/04-audit-trigger/` |
| `05-contenido-lote` | Lote contenido | `sistemas/05-contenido-lote/` |

## Embudo recomendado

```
#1 Audit → #2 Presencia → (#3 Cola ó #4 FAQ/citas según el rubro)
```

## Estado

- **Ahora:** esqueletos en GitHub (1–4 hechos).
- **Después:** import + Meta API + precios reales.
- Login n8n owner: pendiente a propósito.

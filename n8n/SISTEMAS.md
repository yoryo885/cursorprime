# Sistemas n8n — solo diseño (insertar después)

No hace falta login ahora. Acá guardamos **sistemas listos** (JSON) para importar cuando tengas n8n.cloud o VPS.

## Cómo insertarlos después (celular o PC)

1. Abrí tu n8n (cloud o self-host)
2. Menú **⋯** → **Import from File** (o Workflows → Import)
3. Elegí el `.json` de `sistemas/{id}/workflow.json`
4. Completá credenciales marcadas `TODO_CREDENCIAL`
5. **Activate** → copiá la URL del Webhook si aplica

## Catálogo

| ID | Sistema | Para qué | Archivo |
|----|---------|----------|---------|
| `01-ping` | Ping salud | Probar que n8n responde | `sistemas/01-ping/` |
| `02-lead-landing` | Lead de landing | Webhook recibe lead → normaliza → responde OK | `sistemas/02-lead-landing/` |
| `03-wasap-faq` | Wasap FAQ (esqueleto) | Webhook Meta → respuesta FAQ / handoff | `sistemas/03-wasap-faq/` |
| `04-audit-trigger` | Disparo audit | Webhook con URL → log + ack (engancha pipeline luego) | `sistemas/04-audit-trigger/` |
| `05-contenido-lote` | Lote contenido | Webhook con slug → ack para pipeline contenido | `sistemas/05-contenido-lote/` |

## Convención de cada sistema

```
sistemas/{id}/
├── README.md        # qué hace, inputs, outputs, TODOs
└── workflow.json    # importable en n8n
```

## Estado

- **Ahora:** solo archivos en GitHub (versionados).
- **Después:** import + credenciales + Activate.
- Login owner / otro correo: pendiente a propósito.

# Sistemas n8n — diseño sin API (para ver cómo queda)

Importar después en n8n.cloud. **Sin Meta / Shopify / credenciales** por ahora.

## Cómo ver el catálogo

Abrí `catalogo/index.html` (o la URL del tunnel si está servido).

## Ranking 1–8 (negocio)

| # | ID | Qué entrega | Workflows |
|---|-----|-------------|-----------|
| 1 | `06-auditorias-locales` | Informe → planes | 3 |
| 2 | `07-presencia-digital` | Web + GBP | 4 |
| 3 | `08-cola-pedidos-wasap` | Cola pedidos | 4 |
| 4 | `09-wasap-task-faq-citas` | FAQ + citas + handoff | 5 |
| 5 | `10-vertice-pdf-upsell` | PDF + upsell dropship | 4 |
| 6 | `11-kdp-resumenes` | Resumen + listing KDP | 3 |
| 7 | `12-linkedin-ghostwriter` | Pack posts mes | 3 |
| 8 | `13-creador-contenido` | Lote imágenes | 3 |

## Utilitarios

`01-ping` … `05-contenido-lote` — plantillas cortas.

## Embudo

```
#1 Audit → #2 Presencia → (#3 Cola | #4 Wasap task)
#5–#8 = productos / canales propios
```

## Estado

- ✅ Esqueletos 1–8 en GitHub  
- ⏸ Sin API (mock `sin_api: true` en respuestas)  
- ⏸ Login n8n pendiente  

Cuando digas **enchufar APIs**, se conectan Meta / Shopify / runners Cursor.

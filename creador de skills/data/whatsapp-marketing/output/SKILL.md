---
name: whatsapp-marketing
description: >-
  Copy y secuencias WhatsApp para PYMEs: prospección, seguimiento y cierre sin
  Spoki ni APIs externas. Mensajes cortos LATAM. Usar cuando el usuario pide
  whatsapp marketing, whatsapp ventas, secuencia whatsapp, usa
  whatsapp-marketing. Distinto del bot operativo de pedidos.
---

# WhatsApp Marketing

Skill de **capacidad** — scripts comerciales, no integración técnica.

## Cuándo usar

Triggers: whatsapp marketing, whatsapp ventas, secuencia whatsapp, usa whatsapp-marketing.

**No confundir con:**
- `cola-pedidos-whatsapp` — bot operativo / pedidos (idea en `ideas/`)
- Spoki / conectores del video — **descartados** por ahora

## Entregables

Por campaña:

```
## Mensaje 1 (valor, ≤300 chars)
## Mensaje 2 (prueba social)
## Mensaje 3 (CTA suave)
## Follow-up 48h
## Follow-up 7d (opcional)
## Opt-out sugerido
```

## Criterios de calidad

- **≤300 caracteres** por bubble; máx. **3 bubbles** seguidos antes de pausa.
- Tono cercano profesional **LATAM**; sin spam, sin MAYÚSCULAS.
- **CTA suave** — pregunta o invitación, no presión agresiva.
- Horario comercial implícito (no mensajes 23:00).
- Incluir forma de **opt-out** ("si no te interesa, avísame y no te escribo más").
- Personalizar con `{nombre}` y `{negocio}` — no plantilla genérica vacía.

## Secuencias tipo

| Objetivo | Estructura |
|----------|------------|
| Prospección fría | contexto → valor → pregunta abierta |
| Post-lead | agradecer → recurso → CTA llamada |
| Recuperación carrito | recordatorio → beneficio → link |
| Reactivación | novedad → oferta limitada → CTA |

## Viabilidad como proyecto

`ideas/backlog-youtube-viabilidad.json` → **condicional**. Evaluar SaaS WhatsApp con `evaluar-idea` antes de `construye`.

## Gate API

**No** implementar WhatsApp Business API, Twilio o Spoki hasta que el usuario diga `construye` y haya veredicto viable.

## Proyecto

`~/cursorprime/ideas de proyectos`

## Iteración

Ajustar tono en 1 ejemplo de mensaje real del negocio del usuario.

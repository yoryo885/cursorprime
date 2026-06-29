---
name: audit-marketing
description: >-
  Auditoría marketing ligera: competencia, copy, ángulos de ads, SEO básico y
  quick wins en informe markdown. No reemplaza project-lens. Usar cuando el
  usuario pide auditar marketing, audit ecommerce, análisis competencia ads,
  revisar anuncios, usa audit-marketing.
---

# Audit Marketing

Skill de **capacidad** — informe rápido, no due diligence financiera.

## Cuándo usar

Triggers: auditar marketing, audit ecommerce, análisis competencia ads, revisar anuncios, usa audit-marketing.

**Escalar a `project-lens`** si necesitan TAM, márgenes, scores con fuentes.

## Input mínimo

- URL negocio o descripción
- 1–3 competidores (usuario o investigación web)
- Objetivo: leads, ventas, awareness
- Canales actuales conocidos

## Output — `informe-audit.md`

```markdown
# Audit marketing — {marca}
## Resumen ejecutivo (5 líneas)
## 🔴 Crítico (max 3)
## 🟡 Mejora (max 5)
## 🟢 OK
## Competencia (3-5 con URL)
## Ángulos de ads (top 5)
## Copy actual — diagnóstico
## SEO básico (title, meta, 3 keywords)
## Quick wins 7 días
## Siguiente paso recomendado
```

## Criterios

- Cada claim de mercado: `confidence` o fuente URL.
- **No inventar** métricas de ads (CPM, ROAS) sin dato.
- Competencia: nombre + URL + 1 línea de posicionamiento.
- Quick wins = acciones concretas en ≤7 días.
- Si e-commerce: revisar propuesta valor above the fold, no solo SEO técnico.

## Viabilidad como proyecto

`backlog-youtube-viabilidad.json` → **condicional**. Skill para consultas puntuales; producto audit SaaS solo tras `evaluar-idea`.

## Encadenar

`audit-marketing` → (opcional) `landing-lanzamiento` para rediseño copy → (opcional) `project-lens` para viabilidad expandida.

## Proyecto

`~/cursorprime/ideas de proyectos`

## Iteración

Re-audit en 30 días con mismas secciones para comparar.

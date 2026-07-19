# Mejoras UX — benchmark mercado (Jul 2026)

Análisis aplicado al HTML de Vértice Pro (`sitio-pdf` → `proyecto landing/preview`).

## Qué quiere ver la gente (investigación)

| Fuente | Insight clave | Implementado |
|--------|---------------|--------------|
| **Gumroad (146k productos)** | Titular = resultado + persona; 3–5 visuales; descripción por outcomes; garantía visible | Hero outcome, mockup+móvil, compare, garantía 7 días |
| **Shortform / Blinkist** | Personalización, filtros, profundidad vs resumen superficial; comparar con suscripción | Filtro rol×libro, tabla vs suscripción, plan 10 semanas |
| **Gumroad pricing UX** | Compra única = decisión fácil; anclar vs $15–20/mes | Strip compare + CTA «desde $4.99» |
| **Landing SaaS 2026** | Problema primero; «para quién es»; 3 pasos; prueba social con rol | `hero-problem`, roles grid, pasos, testimonios |
| **Filjos (referencia diseño)** | Crema/dorado, grid limpio | Paleta y tipografía mantenidas |

## Orden de secciones (conversión)

1. **Hero** — dolor + resultado + mockup + carrusel libros
2. **Compare** — vs Blinkist/Shortform (compra única)
3. **Trust badges** — PDF, instante, plan, rol
4. **Cómo funciona** — 3 pasos
5. **Para quién es** — roles clicables → catálogo filtrado
6. **Preview** — mockup + semanas del plan
7. **Catálogo** — destacada + filtros + grid
8. **Qué incluye** — 3 benefits + plan 10 semanas
9. **Opiniones** — testimonios con rol
10. **FAQ + garantía**
11. **Newsletter + sticky CTA móvil**

## Regenerar

```bash
cd sitio-pdf
python3 sitio_pdf_main.py generar --slug vertice-pro --producto pareto --mock --reset-checkpoint
bash "../proyecto landing/scripts/sync-desde-pipeline.sh"
```

Fuente: `marca.json` → `ux_landing` + `assembler_agent.py`

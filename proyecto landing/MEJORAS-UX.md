# Mejoras UX — benchmark nicho (Jul 2026)

Investigación aplicada automáticamente al HTML de preview.

## Referencias analizadas

| Plataforma | Qué les gusta a los usuarios | Aplicado en Vértice Pro |
|------------|------------------------------|-------------------------|
| **Shortform / getAbstract** | PDF descargable, valor profesional, sin leer el libro entero | Badges «PDF · Sin suscripción» + FAQ comparando con suscripción |
| **Blinkist** | Personalización por interés, carruseles, filtro por categoría | Filtro dual rol + libro; carrusel → «Ver guías de este libro» |
| **Ebook landings (Seedprod, Swipe Pages)** | Bullets de beneficio, mockup, FAQ, formulario corto, CTA sticky | Hero bullets, FAQ accordion, newsletter email, barra sticky móvil |
| **Filjos (referencia diseño)** | Grid limpio, crema/dorado, sin ruido | Mantenido; separación Disponibles / Próximamente |

## Interacciones nuevas

1. **Carrusel (libros)** → botón lleva al grid filtrado por libro
2. **Filtro rol** + **filtro libro** combinables
3. **Grids separados**: disponibles arriba, próximamente abajo
4. **Sticky CTA** en móvil al hacer scroll
5. **Sección Qué incluye** con plan 10 semanas

## Regenerar

```bash
bash "proyecto landing/scripts/sync-desde-pipeline.sh"
```

Fuente: `sitio-pdf/src/agents/assembler_agent.py` + `marca.json` → `ux_landing`

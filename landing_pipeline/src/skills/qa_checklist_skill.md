# Skill: QA checklist

## Regla
Puntuar conversión. Texto/línea exacta. Críticos bloquean.
Chequeos automáticos obligatorios.

## Chequeos automáticos
1. Palabras repetidas (`desde desde`) → crítico.
2. Acento único: `.btn` → `var(--accent)`; sin `.btn-dark`.
3. Naming: `nombre_producto` en title/hero/footer; no `producto_interno` en FAQ.
4. Overlap CSS: absolute/fixed fuera de header → crítico.
5. Secciones: cada `data-section` de SECTION_ORDER cuenta exactamente 1 (o 0 si omitida).
6. Similitud de texto >70% entre secciones distintas (salvo hero≈cta_final) → crítico.
7. Testimonios: `omitida:true` + registro en `omisiones`.
8. Sin animaciones scroll-reveal / opacity:0+translateY.
9. **CTA ≥ 3** botones `.btn` (hero, mid beneficios, precio/cta).
10. **Garantía** visible (`class="garantia"`) bajo el CTA de precio.
11. **FAQ** incluye pregunta de garantía/riesgo/devolución.

## Output esperado (JSON)
{
  "score": 0,
  "criticos": [],
  "sugerencias": [],
  "regenerar": [],
  "omisiones": [],
  "bugs_v2": {},
  "section_counts": {},
  "cta_count": 0
}

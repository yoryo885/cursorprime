# Skill: QA checklist

## Regla
Puntuar conversión. Marcar sección que falla con texto/línea exacta.
Errores críticos bloquean. Incluir chequeos automáticos (regex/parsing).

## Checklist (errores que matan conversión)
1. Botón que no destaca (contraste / tamaño).
2. Más de un mensaje principal en el hero.
3. Texto largo donde debería ir imagen / visual.
4. Formulario largo antes de generar confianza.
5. Precio oculto o con letra chica.
6. Testimonios inventados o genéricos.
7. CTA genérico ("Enviar", "Click aquí").
8. Más de 8 secciones / desorden visual.
9. Sin versión mobile usable.
10. Claims sin fuente marcados como alta confianza.

## Chequeos automáticos (obligatorios — bugs reales)
1. **Palabras repetidas**: patrón `\b(\w+)\s+\1\b` en texto visible (ej. "desde desde") → crítico + texto exacto.
2. **Acento único**: todos los `.btn` primarios resuelven a `var(--accent)`; no `.btn-dark` con otro background.
3. **Naming**: `nombre_producto` del brief igual en `<title>`, hero brand y footer; no filtrar `producto_interno`.
4. **Overlap CSS**: `position: absolute|fixed` fuera de header/nav → crítico.
5. **Secciones**: esperadas vs presentes; si falta sin `omitida` en copy → crítico.
6. **Testimonios**: si no hay data → debe existir `omitida: true` en copy y registro en `omisiones` del qa_report (no silenciar).

## Scoring
- 90–100: listo
- 70–89: ajustes menores
- <70: regenerar secciones marcadas

## Output esperado (JSON)
{
  "score": 0,
  "criticos": [],
  "sugerencias": [],
  "regenerar": [],
  "omisiones": [],
  "bugs_v2": {}
}

# Skill: QA checklist

## Regla
Puntuar conversión. Marcar sección que falla. Errores críticos bloquean.

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

## Scoring
- 90–100: listo
- 70–89: ajustes menores
- <70: regenerar secciones marcadas

## Output esperado (JSON)
{
  "score": 0,
  "criticos": [],
  "sugerencias": [],
  "regenerar": []
}

# Skill: QA Checklist

## Regla
Revisa el guion completo contra errores que matan retención. Puntúa y marca qué agente regenerar.

## Obligatorio — fallos graves
- Intro larga o saludo al inicio.
- Sin texto en pantalla.
- Plano fijo más de 4–5 segundos sin interrupt.
- CTA ausente o apurado al final.
- Loop que no conecta con el hook.
- Hashtags genéricos (#fyp, #viral).
- Más de un mensaje central en el script.

## Scoring
- 90–100: listo para grabar
- 70–89: ajustes menores
- <70: regenerar agentes marcados

## Output esperado (JSON)
{ "score": 0, "ok": false, "issues": [{"agente": "", "detalle": ""}], "regenerar": [] }

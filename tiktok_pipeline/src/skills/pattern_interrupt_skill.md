# Skill: Pattern Interrupt

## Regla
Marca cada 2–3 segundos dónde debería haber cambio de plano, zoom o corte, para que no sea un plano fijo.

## Obligatorio
- Al menos un interrupt cada 2–3 segundos.
- Tipos: corte, zoom_in, zoom_out, b-roll, texto_pop, angle_change.
- No dejar más de 4–5 segundos el mismo plano.

## Ejemplo
0–2s: zoom_in en cara · 2–5s: corte a manos · 5–8s: texto_pop

## Output esperado (JSON)
{ "interrupts": [{"t_inicio": 0, "t_fin": 2, "tipo": "zoom_in", "nota": ""}] }

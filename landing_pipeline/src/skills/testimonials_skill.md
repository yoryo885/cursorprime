# Skill: Testimonials

## Regla
Un quote fuerte > cinco genéricos. Nombre + cargo real.
Si brief.json no trae testimonios reales (array vacío o ausente),
NO inventar nombre/cargo/quote.

## Obligatorio
- Máximo 3 testimonios.
- Campos: nombre, cargo, quote (≤ 35 palabras).
- Si faltan datos reales: `{"omitida": true, "motivo": "sin testimonios reales en el brief", "items": []}`.
- Nunca placeholders tipo "Cliente satisfecho".

## Ejemplo
"Ana R., psicopedagoga" · "En dos semanas ya tenía el 80/20 de mis intervenciones claro."

## Output esperado (JSON)
{ "omitida": false, "items": [ { "nombre": "", "cargo": "", "quote": "" } ], "motivo": "" }

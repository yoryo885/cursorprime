# Skill: Testimonials

## Regla
Un quote fuerte > cinco genéricos. Nombre + cargo real.
Si no hay testimonios reales: NO inventar; devolver lista vacía y nota.

## Obligatorio
- Máximo 3 testimonios.
- Campos: nombre, cargo, quote (≤ 35 palabras).
- Si faltan datos reales: `"items": []`, `"nota": "sin testimonios reales"`.

## Ejemplo
"Ana R., psicopedagoga" · "En dos semanas ya tenía el 80/20 de mis intervenciones claro."

## Output esperado (JSON)
{ "items": [ { "nombre": "", "cargo": "", "quote": "" } ], "nota": "" }

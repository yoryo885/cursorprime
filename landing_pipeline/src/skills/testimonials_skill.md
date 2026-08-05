# Skill: Testimonials

## Regla
Un quote fuerte > cinco genéricos. Nombre + cargo/ciudad real.
Si no hay data: `omitida: true` (no inventar).

## Obligatorio
- Máx. 3. Si faltan: `{"omitida": true, "motivo": "sin testimonios reales en el brief", "items": []}`.
- Formato creíble: quote corto + nombre de pila + ciudad o rol (ej. "Hrefna, Akureyri").
- Nunca "Cliente satisfecho".

## Output esperado (JSON)
{ "omitida": false, "items": [ { "nombre": "", "cargo": "", "quote": "" } ], "motivo": "" }

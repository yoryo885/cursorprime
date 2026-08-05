# Skill: Pricing

## Regla
Precio claro, sin letra chica, un solo CTA de compra.
Debajo del botón: línea de garantía / reversión de riesgo (obligatoria).

## Obligatorio
- Precio visible. Sanitizar "desde" / "a partir de" (nunca duplicar).
- 3 bullets máx. de qué incluye.
- Un CTA de compra.
- Campo `garantia` justo bajo el botón (ej. "Pago único, sin suscripción").

## Ejemplo
"desde $4.99" · [Comprar] · "Pago único · acceso inmediato · sin letra chica"

## Output esperado (JSON)
{ "precio": "", "incluye": ["", "", ""], "cta": "", "garantia": "" }

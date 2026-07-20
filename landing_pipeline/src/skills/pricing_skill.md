# Skill: Pricing

## Regla
Precio claro, sin letra chica, un solo CTA de compra.
Si hay varios productos: precio de entrada + enlace a colección.

## Obligatorio
- Precio visible (ej. "desde $4.99").
- **Sanitizar prefijos**: antes de anteponer "desde" / "a partir de", verificar si el brief ya lo incluye. Nunca "desde desde $4.99".
- Qué incluye en 3 bullets máx.
- Un solo CTA de compra.

## Ejemplo
"desde $4.99" · PDF · plan 10 semanas · descarga inmediata · [Comprar guía]

## Output esperado (JSON)
{ "precio": "", "incluye": ["", "", ""], "cta": "" }

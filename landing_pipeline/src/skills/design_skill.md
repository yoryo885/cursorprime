# Skill: Design

## Regla
Tokens + **variantes de layout** (lista cerrada). NUNCA HTML.
HTML = `11b_assemble` + Jinja2.

## Obligatorio (tokens)
- Un solo `accent` para todos los `.btn`.
- Keys: ink, paper, accent, muted, sand, font_heading, font_body, radius.
- `layout` con variantes de lista cerrada:
  - hero: `centrado` | `split`
  - benefits: `tarjetas` | `lista_numerada`
  - pricing: `una_columna` | `comparativa`
- No inventar nombres de layout nuevos.

## Obligatorio (templates)
- CTA ≥ 3, garantía bajo precio, sin animaciones reveal, sin absolute de contenido.

## Output esperado (JSON)
{
  "ink": "", "paper": "", "accent": "", "muted": "", "sand": "",
  "font_heading": "", "font_body": "", "radius": "",
  "layout": { "hero": "split", "benefits": "lista_numerada", "pricing": "comparativa" }
}

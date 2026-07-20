# Skill: Design

## Regla
Tokens de diseño (colores, tipografía, radios) — NO HTML.
HTML = `11b_assemble` + Jinja2.

## Obligatorio (tokens)
- Un solo `accent` para todos los botones primarios.
- Keys: ink, paper, accent, muted, sand, font_heading, font_body, radius.

## Obligatorio (templates)
- CTA primario ≥ 3 veces (hero, después de beneficios, precio y/o CTA final). Todas con `var(--accent)`.
- Sin absolute/fixed de contenido; sin animaciones scroll-reveal.
- Garantía visible bajo el botón de precio.
- Testimonios omitidos → no renderizar template.

## Output esperado (JSON tokens)
{ "ink": "", "paper": "", "accent": "", "muted": "", "sand": "", "font_heading": "", "font_body": "", "radius": "" }

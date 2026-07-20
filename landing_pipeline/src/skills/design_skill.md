# Skill: Design

## Regla
Tokens de diseño (colores, tipografía, radios) — NO HTML.
El HTML lo arma `11b_assemble.py` con Jinja2 (determinístico).

## Obligatorio (tokens)
- Un solo `accent` para todos los botones primarios.
- `ink`, `paper`, `accent`, `muted`, `sand`, `font_heading`, `font_body`, `radius`.

## Obligatorio (templates / assemble — no el LLM)
- Un solo `landing.html` vía templates Jinja2.
- `--accent` una vez en `:root`; todo `.btn` usa `var(--accent)`.
- Cada sección: flujo normal, sin `position: absolute|fixed` de contenido.
- **Sin animaciones de entrada** (no IntersectionObserver, no opacity:0 + translateY).
- Si testimonios `omitida`, no incluir el template.

## Output esperado (JSON tokens)
{ "ink": "", "paper": "", "accent": "", "muted": "", "sand": "", "font_heading": "", "font_body": "", "radius": "" }

# Skill: Design

## Regla
HTML/CSS en un solo archivo, mobile-first.
Un acento para botones. Jerarquía tipográfica clara.
Paleta según rubro (confianza / editorial / retail).

## Obligatorio
- Un solo `landing.html` autocontenido.
- CSS variables en `:root`: `--ink`, `--paper`, `--accent`, `--muted`.
- **Un solo color de acento** (`--accent`). Todo botón primario / CTA usa `background: var(--accent)`. Prohibido `.btn-dark` u otro color de botón primario por sección.
- Hero: marca = `nombre_producto` del brief + 1 título + 1 bajada + 1 CTA.
- Cada `<section>` es flujo normal: sin `position: absolute` ni `fixed` para contenido de texto; sin `z-index` negativo; sin animaciones que dejen dos secciones en el mismo espacio. Solo el header/nav puede ser `sticky`/`fixed`.
- Fondo opaco por sección (no transparencia que deje ver la sección contigua).
- Tipografía expresiva (no Inter/Roboto/Arial como display).
- Responsive desktop + mobile.
- Si `testimonials.omitida === true`, NO renderizar la sección (la omisión la registra QA).

## Paleta ejemplo (editorial / educación)
- ink: #1b222c
- paper: #f4f1ec
- accent: #c9a962 (botones)
- muted: #7a847c

## Output esperado
Archivo HTML completo. No JSON de copy (ya viene en copy.json).

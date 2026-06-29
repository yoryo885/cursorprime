---
name: landing-lanzamiento
description: >-
  Funnel de lanzamiento: estratega oferta, copy y wireframe markdown para
  landing (hero, beneficios, prueba social, CTA). Sin hosting ni skills
  externas. Usar cuando el usuario pide landing, lanzamiento, oferta, página
  ventas, copy lanzamiento, usa landing-lanzamiento.
---

# Landing Lanzamiento

Skill de **workflow** — copy + estructura, no constructor web.

## Cuándo usar

Triggers: landing, lanzamiento, oferta, página ventas, copy lanzamiento, usa landing-lanzamiento.

**No es** agencia web 10k€ (#6 videos) — es entregable **`landing-brief.md`** listo para Webflow, Framer o HTML manual.

## Pasos

1. **Brief**: producto, avatar, dolor, precio/CTA, prueba social disponible, objeciones conocidas.
2. **Estratega (chat)** — output:
   - Propuesta de valor en 1 frase
   - 3 objeciones + respuesta
   - Orden de secciones (máx. 7)
3. **Copy (chat)** — por sección:
   - Hero: headline ≤10 palabras, subhead, CTA primario
   - Beneficios: 3 bullets con resultado medible
   - Prueba social: testimonio o dato citado
   - CTA final + garantía
4. **Opcional prompts pack**:
   ```bash
   cd ~/cursorprime/creador\ de\ prompts
   python3 creador_prompts_main.py --slug {slug}-landing --tipo marketing
   ```
5. **Entregar** `landing-brief.md`:

```markdown
# {Producto} — Landing brief
## Hero | ## Problema | ## Solución | ## Beneficios | ## Prueba | ## FAQ | ## CTA
```

## Criterios de calidad

- **1 CTA principal** repetido 2–3 veces.
- Hero legible en 5 segundos (headline + sub + botón).
- Objeciones respondidas **antes** del CTA final.
- Sin fluff corporativo; específico al avatar.
- No inventar testimonios — marcar `[PENDIENTE: testimonio real]`.

## Viabilidad como proyecto

Ver `ideas/backlog-youtube-viabilidad.json` → **condicional**. Skill basta para MVP; pipeline web solo con clientes recurrentes.

## Encadenar

`evaluar-idea` (si negocio nuevo) → `landing-lanzamiento` → diseño manual o dev externo.

## Proyecto

General · Prompts: `creador de prompts` tipo `marketing` / `copy`

## Iteración

A/B: 2 headlines en hero; usuario elige antes de publicar.

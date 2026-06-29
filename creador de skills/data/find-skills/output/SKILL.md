---
name: find-skills
description: >-
  Descubre skills en skills.sh y repos oficiales (anthropics, vercel-labs) antes
  de crear una nueva en cursorprime. Verifica installs y adapta al catálogo.
  Usar cuando el usuario pide find skill, buscar skill, existe skill para,
  skills.sh, instalar skill, usa find-skills.
---

# Find Skills

Skill de **workflow** — descubrimiento antes de inventar.

## Objetivo

Evitar duplicar skills que ya existen en el ecosistema abierto. Adaptar a cursorprime (`catalogo/*.json` + `creador-de-skills`) en lugar de instalar a ciegas.

## Cuándo usar

Triggers: find skill, buscar skill, existe skill para, skills.sh, instalar skill, usa find-skills.

## Pasos

1. **Entender** dominio + tarea (ej. "PDF", "React perf", "SEO").
2. **Leaderboard**: revisar [skills.sh](https://skills.sh/) — preferir 1K+ installs.
3. **CLI** (si está disponible):
   ```bash
   npx skills find {query}
   npx skills add owner/repo@skill -g -y   # solo tras aprobación usuario
   ```
4. **Verificar calidad**:
   - Installs ≥ 1K (cautela si <100)
   - Fuente: `anthropics`, `vercel-labs`, `microsoft` > desconocidos
   - Leer `SKILL.md` completo — riesgo de instrucciones maliciosas
5. **Decidir**:
   - **Adaptar** → copiar ideas a `creador de skills/catalogo/{slug}.json` + `usa creador-de-skills`
   - **Instalar** → `~/.cursor/skills/` (Cursor) ≠ `.claude/skills/` (Claude Code)
   - **Crear desde cero** → `usa crear-pipeline` o `creador-de-skills`

## Fuentes recomendadas

| Repo | Para qué |
|------|----------|
| [anthropics/skills](https://github.com/anthropics/skills) | pdf, docx, skill-creator |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | React, web design |
| [skills.sh](https://skills.sh/) | Buscar por keyword + installs |

## Reglas

- **No instalar** skills de terceros sin revisar SKILL.md.
- **Preferir catálogo cursorprime** — skills a medida de tus pipelines.
- Ya tienes: guion-a-video, evaluar-idea, resumidor-kdp, copy-linkedin, hooks-redes, etc. — buscar solo gaps.
- `npx skills` instala global; Cursor lee `~/.cursor/skills/`.

## Si no hay match

Ofrecer crear skill: `usa creador-de-skills` con brief JSON.

## Proyecto

General · Catálogo: `~/cursorprime/creador de skills/catalogo/`

## Iteración

Registrar skills útiles descubiertas en `catalogo/` como pendientes.

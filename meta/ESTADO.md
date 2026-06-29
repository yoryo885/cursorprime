# cursorprime — Estado del ecosistema

Actualizado: 2026-06-27

Referencia rápida para agentes y usuarios: qué está listo y qué falta.

## Menú de productos

### Video o imágenes — guion, escenas, animación

- [x] Skill `guion-a-video` instalado
- [x] Pipeline `creador de contenido/creador_imagenes_main.py`
- [x] Demos (`demo_animado`, `demo_slideshow`, `demo_full`, `demo_lote`)
- [ ] Video animado con API Kling real (requiere `.env`; mock: `MOCK_KLING=true`)

### Libro o PDF — resumen, listing KDP

- [x] Skill `resumidor-kdp` instalado
- [x] `libros a entender/main.py` (resumen editorial)
- [x] `libros a entender/kdp_main.py` (listing Amazon)
- [x] Skill `pdf-resumidor` (PDFs genéricos, no solo libros)
- [ ] Correr con un PDF concreto del usuario

### Idea de proyecto — viabilidad, análisis

**Rápido** (`evaluar-idea` → `ideas de proyectos/evaluar.py`):

- [x] Skill instalado
- [x] `evaluar.py` + spec `EVALUADOR.md`
- [x] 3 evaluaciones hechas (`wasap_pymes`, `contenido_creativo`, cola WhatsApp)
- [x] Gate: no construir en `proyectos/` hasta «construye» / «armado» / «crea el proyecto»

**Profundo** (`project-lens` → `project_lens/`):

- [x] Skill instalado
- [x] Pipeline Python con 13 agentes (`project_lens_main.py`)
- [x] Modo MVP (8 agentes, mock web) — probado `demo-idea`
- [x] Modo full (13 agentes) — probado `wasap-pymes`
- [x] V2 compare y `--aplicar-mejoras`
- [ ] V1 web real (`--no-mock-web` + Playwright + `MOCK_WEB=false`) — requiere setup local
- [ ] Correr análisis profundo para una idea nueva del usuario

### LinkedIn — posts al estilo del perfil

- [x] Skill `copy-linkedin` instalado
- [x] `linkedin-ghostwriter/generar_posts.py`
- [ ] Generar posts de un mes concreto (input del usuario)

### Prompts o skills — plantillas y flujos en Cursor

- [x] Skill `creador-de-prompts` + pipeline
- [x] Skill `creador-de-skills` + pipeline
- [x] Skill `cursorprime-router` (enrutamiento automático)
- [x] Skill `crear-pipeline` (cola #5 completada)
- [x] Skill `pipeline-project-creator` (scaffolding alternativo)

### Workspace — documentación y router

- [x] `AGENTS.md`, `COMO_ABRIR.md`, `router.py`, `meta/router.json`
- [x] Regla `.cursor/rules/cursorprime.mdc`
- [x] Este archivo (`meta/ESTADO.md`)

## Cola de skills

| # | Skill | Estado |
|---|-------|--------|
| 1 | guion-a-video | hecho |
| 2 | evaluar-idea | hecho |
| 3 | resumidor-kdp | hecho |
| 4 | copy-linkedin | hecho |
| 5 | crear-pipeline | hecho |

## Router → skill (viabilidad)

| Intención | Ruta | Skill | CLI |
|-----------|------|-------|-----|
| viabilidad, evaluar idea | `evaluar-idea-rapido` | `evaluar-idea` | `ideas de proyectos/evaluar.py` |
| análisis profundo, competencia | `evaluar-idea-profundo` | `project-lens` | `project_lens/project_lens_main.py` |

## Flujo recomendado para ideas

```
Idea → evaluar.py (rápido) → project_lens (profundo, opcional) → construye (gate)
```

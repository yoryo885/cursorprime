# cursorprime

Ecosistema de pipelines con agentes. **Un solo workspace para todo** (excepto linkedin-ghostwriter si lo abres aparte).

**Abrir en Cursor:** `File → Open Workspace → cursorprime.code-workspace`  
Guía paso a paso: [COMO_ABRIR.md](./COMO_ABRIR.md)

## Proyectos

| Carpeta | Descripción |
|---------|-------------|
| [creador de prompts](./creador%20de%20prompts/) | Prompts compartidos |
| [creador de skills](./creador%20de%20skills/) | **Skills Cursor** — genera SKILL.md |
| [creador de contenido](./creador%20de%20contenido/) | Pipeline PNG · GIF · Video · PDF |
| [libros a entender](./libros%20a%20entender/) | Herramientas y flujos para analizar y entender libros/PDFs |
| [ideas de proyectos](./ideas%20de%20proyectos/) | Evaluación rápida de ideas (`evaluar.py`) |
| [analisis-de-proyectos](./analisis-de-proyectos/) | **Análisis** YouTube/web → crear proyectos |
| [marketing-audit](./marketing-audit/) | **Audit web** — 5 agentes paralelos → score + PDF |
| [lluvia-de-ideas](./lluvia-de-ideas/) | Propuestas + tu OK (cola) |
| [centro de control prime](./centro%20de%20control%20prime/) | **Panel** — inventario y stats del ecosistema ($0 local) |
| [project_lens](./project_lens/) | Análisis profundo — 13 agentes, mercado, finanzas, QC |
| [linkedin-ghostwriter](./linkedin-ghostwriter/) | **Proyecto aparte** — posts de LinkedIn (no comparte pipelines) |

Estado hecho/pendiente: [meta/ESTADO.md](./meta/ESTADO.md)

## Organización en Cursor

```
cursorprime/              ← único workspace
├── Explorer (⌘⇧E)        ← carpetas y código
└── Agents                ← chats por módulo (imagenes, gifs, video…) — conserva el contexto de cada pieza
```

El ecosistema multimedia se llama **creador de contenido** (antes *creador de imagenes 1* en algunos chats).

## Enrutamiento automático

Di lo que quieres en lenguaje natural — el agente elige skill y prompt:

```bash
python3 router.py --texto "quiero un video de pareto"
```

Reglas: `meta/router.json` · Skill: `cursorprime-router`

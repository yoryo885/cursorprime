---
name: crear-pipeline
description: >-
  Entry point cursorprime para diseñar y construir pipelines Python con agentes,
  CLI, checkpoints y QC. Lee pipeline-project-creator y copia el patrón de
  creador de prompts / creador de skills. Usar cuando el usuario pide crear
  pipeline, nuevo pipeline, scaffolding agentes, meta/plan.json, usa
  crear-pipeline, o pipeline python.
---

# Crear Pipeline Python

Extiende **pipeline-project-creator** con contexto y referencias de cursorprime.

## Primer paso (obligatorio)

Leer `~/.cursor/skills/pipeline-project-creator/SKILL.md` — spec completa de fases, plantillas y Definition of Done.

**Alias:** `usa crear-pipeline` = `usa pipeline-project-creator` en cursorprime. Esta skill añade rutas y ejemplos del ecosistema.

## Cuándo usar

Triggers: crear pipeline, nuevo pipeline, scaffolding agentes, usa crear-pipeline, pipeline python.

| Pedido | Modo |
|--------|------|
| Proyecto nuevo desde cero | Modo A |
| Mejorar pipeline existente | Modo B |
| Módulo paralelo (ej. marketing vs producción) | Modo C |

## Referencias vivas en cursorprime

Copiar estructura y convenciones de:

| Proyecto | Qué copiar |
|----------|------------|
| `creador de prompts` | 6 agentes, `data/{slug}/`, QC, packager |
| `creador de skills` | Catálogo JSON, cola, instalación a `~/.cursor/skills/` |
| `libros a entender` | Pipelines paralelos (`main.py` + `kdp_main.py`) |
| `ideas de proyectos` | Evaluador ligero + gate de construcción |

## Modo A — Proyecto nuevo

### Fase 1: Brief (YAML)

```yaml
nombre_proyecto:
slug:
problema:
usuario_final:
entrada:
salida:
integraciones:
restricciones:
```

Máximo 3 preguntas críticas. Inferir el resto y documentar supuestos.

### Fase 2: Pipeline (5–12 pasos)

Cada paso: `id`, `slug`, `nombre`, `agente`, `input`, `output`, `puede_fallar`, `flag_cli`.

Siempre: **Context/Loader** → pasos de negocio → **QC** → **Packager**.

Diagrama mermaid obligatorio antes de Fase 3.

### Fase 3: Estructura

```
{proyecto}/
├── {slug}_main.py
├── requirements.txt
├── .env.example
├── PROYECTO.md
├── meta/plan.json
├── meta/constitution.json
├── data/{slug}/inputs/
├── data/{slug}/meta/
├── data/{slug}/output/
├── logs/errores.json
└── src/{config,pipeline,checkpoint,types,agents/}
```

### Fase 4: Scaffolding ⚠️ gate

**Solo si el usuario dice:** `construye`, `armado`, `fase 4`.

- Orquestador + checkpoint + agentes stub (mock OK)
- CLI: `--slug`, `--reset-checkpoint`, `--solo-{paso}`, `--sin-{paso}`
- `python3 {slug}_main.py --help` debe funcionar
- Sin lógica de negocio pesada en MVP

### Fase 5: Plan de implementación

Checklist MVP / V1 / futuro en `PROYECTO.md`. Confirmar antes de APIs de pago.

## Modo B — Mejorar existente

1. Auditar `PROYECTO.md`, `meta/plan.json`, `src/pipeline.py`, `logs/`
2. Diagnóstico: 🔴 crítico / 🟡 mejora / 🟢 nice-to-have
3. Diff mínimo por archivo
4. Actualizar `plan.json` + `logs/mejoras.json`

## Modo C — Pipeline paralelo

Segundo entrypoint (`{modulo}_main.py`) que **solo lee** outputs del pipeline principal. Ejemplo: `kdp_main.py` en libros a entender (marketing vs producción).

## Reglas cursorprime

- **No construir** sin autorización explícita.
- **Un CLI principal** por pipeline.
- **QC antes de packager** — rechazar entregables inválidos.
- **Estado JSON** en disco, no solo en memoria del chat.
- **Sin commits** salvo que el usuario lo pida.
- Registrar errores en `logs/errores.json`.

## Definition of Done

- [ ] `--help` funciona
- [ ] Pipeline end-to-end con datos mock
- [ ] Checkpoint reanuda desde paso intermedio
- [ ] QC detecta al menos 1 error de prueba
- [ ] `PROYECTO.md` usable sin leer código
- [ ] `.env.example` completo

## Stack por defecto

Python 3.9+, argparse, python-dotenv, JSON en disco. Claude si LLM. Playwright si bot/scraper.

## Proyecto

General (nuevo bajo `~/cursorprime/` o ruta que indique el usuario).

## Iteración

Si el diseño no encaja, volver a Fase 2 (pipeline) antes de tocar código.

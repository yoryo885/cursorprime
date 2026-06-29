---
name: gestion-proyecto
description: >-
  Gestiona proyectos reales con sistema documentado: brief, evaluación opcional,
  PROYECTO.md y plan antes de código, gate construye, checkpoints y QC. Sin
  plantillas externas. Usar cuando el usuario pide gestionar proyecto, proyecto
  real, documentar proyecto, usa gestion-proyecto, yo sa, o construir algo que
  funcione de verdad.
---

# Gestión Proyecto

Skill de **workflow** — metodología **sistema > prompts** (inspirada en gestión de proyectos reales con IA, reinventada para cursorprime).

## Cuándo usar

Triggers: gestionar proyecto, proyecto real, documentar proyecto, usa gestion-proyecto, yo sa, sistema proyecto.

**Antes de `crear-pipeline`** si el alcance aún está difuso.

## Fases

### Fase 0 — Brief

YAML o JSON en `ideas de proyectos/ideas/{slug}.json`:

```yaml
nombre:
slug:
problema:
usuario_final:
entrada:
salida:
integraciones:
restricciones:
```

Máx. 3 preguntas al usuario. Inferir el resto y documentar supuestos.

### Fase 1 — Evaluar (si es negocio)

```bash
cd ~/cursorprime/ideas\ de\ proyectos
python3 evaluar.py ideas/{slug}.json
```

Si `descartar` → parar. Si `condicional` → acotar MVP. Si `viable` → Fase 2.

### Fase 2 — Documentación (sin código)

Crear en la carpeta del proyecto futuro:

- `PROYECTO.md` — qué hace, comandos, estructura
- `meta/plan.json` — pasos del pipeline
- `meta/constitution.json` — reglas inmutables

Diagrama mermaid del flujo. **Cero código de negocio** en esta fase.

### Fase 3 — Gate construcción

Esperar: `construye`, `armado`, `fase 4`.

Entonces: **`usa crear-pipeline`** → scaffolding MVP.

### Fase 4 — Seguimiento

- Checkpoints en `meta/.checkpoint.json`
- Errores en `logs/errores.json`
- Cerrar cada fase actualizando `PROYECTO.md`

## Encadenar cursorprime

```
gestion-proyecto → evaluar-idea → crear-pipeline → creador-de-prompts / creador-de-skills
```

## Reglas

- No escribir código hasta Fase 2 completa + gate.
- `PROYECTO.md` usable sin leer `src/`.
- TODOs visibles por agente/paso.
- No descargar plantillas de cursos/videos — copiar patrón de `creador de prompts` o `creador de skills`.

## Proyecto

General · Backlog ideas: `ideas de proyectos/BACKLOG_VIABILIDAD.md`

## Iteración

Al terminar MVP, Modo B de `crear-pipeline` para mejoras.

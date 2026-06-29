---
name: evaluar-idea
description: >-
  Evalúa viabilidad de una idea de negocio con evaluar.py (rápido, local): veredicto,
  score, margen en rango y confidence. Complementa con project-lens si hace falta
  investigación de mercado. Proyecto: Ideas de proyectos. Usar cuando el usuario
  pide evaluar idea, viabilidad, antes de construir, usa evaluar-idea, o quiere
  veredicto viable/condicional/descartar sin abrir pipeline nuevo.
---

# Evaluar Idea

Skill de **workflow** para Ideas de proyectos.

## Cuándo usar

Activar cuando el usuario diga: evaluar idea, viabilidad, usa evaluar-idea, antes de construir.

**No confundir con `project-lens`:** evaluar-idea = evaluación rápida con `evaluar.py`. project-lens = investigación profunda con agentes y web (usar solo si confidence bajo o el usuario pide análisis exhaustivo).

## Proceso

Evalúa viabilidad con veredicto, márgenes de error y confidence. Primero `evaluar.py`; complementar con project-lens si faltan datos de mercado.

## Pasos

1. **Recibir idea**: JSON en `ideas/` o texto libre. Confirmar slug y título.
2. **Ejecutar evaluador**:
   ```bash
   cd ~/cursorprime/ideas\ de\ proyectos
   python3 evaluar.py ideas/{archivo}.json
   python3 evaluar.py --texto "Descripción de la idea..."
   python3 evaluar.py listar
   ```
3. **Revisar salida**: `evaluaciones/{slug}/veredicto.json` e `informe.md`.
4. **Profundizar (opcional)**: si `confidence` ≤ 0.5 o el usuario pide mercado real → `usa project-lens`.
5. **Entregar**: veredicto, score, margen (min–max), riesgos top 3, `siguiente_paso`. **No construir** código hasta que diga: construye / armado / crea el proyecto.

## Reglas

- No inventar cifras de mercado — `confidence` ≤ 0.5 si no hay fuentes.
- Margen siempre en rango `min`/`max`, nunca punto único.
- Veredicto: `viable` (≥65) / `condicional` (40–64) / `descartar` (<40).
- Evaluar **antes** de abrir ramas nuevas (libros a entender, proyectos/x, etc.).
- Ruta base: `~/cursorprime/ideas de proyectos`

## Proyecto

Carpeta: `../ideas de proyectos` · Spec: `EVALUADOR.md` · Ejemplo: `ideas/ejemplo-idea.json`

## Iteración

Si el resultado no encaja, pedir feedback y actualizar esta skill (v2 en misma carpeta).

# Prompts — PDF + guiones de video en creador de contenido

- **Tipo:** cursor
- **Proyecto:** creador-de-contenido
- **Estado:** pendiente (`meta/pendientes.json`)
- **Generado:** 2026-06-27

## Extender módulo PDF → también genera guiones de video (v1)

Copia y pega en Cursor con el workspace **creador de contenido** abierto:

```
Actúa como agente del proyecto **Creador de Contenido** (`~/cursorprime/creador de contenido`).

## Problema

Hoy el módulo PDF (`pdf/agent.py` → `PdfModule`) solo maqueta PNGs en un `.pdf` con reportlab. Los guiones de video viven aparte: el usuario debe poner `guion` o `escenas` en `lote.json` y activar modo `video` animado para que `EscenasAgent` genere `meta/escenas.json`.

Queremos que la salida PDF **también** pueda crear guiones para video — no limitarse al documento.

## Objetivo

Cuando un lote pida salida `pdf` (o `pdf` + `video`), además del `.pdf` generar un **guion estructurado** reutilizable por el pipeline de video animado existente.

## Estado actual (no reinventar)

- `PdfModule`: compila PNG + título → `data/{slug}/pdf/{slug}.pdf`
- `EscenasAgent`: divide `guion` en escenas con prompts de frame inicio/fin/animación → `meta/escenas.json`
- `VideosModule` modo animado: consume escenas + frames PNG → clips → MP4
- Entrada típica: `data/{slug}/inputs/lote.json` con `temas`, `salidas`, opcional `guion`

## Qué implementar (MVP incremental)

1. **Extender salida del módulo PDF** (o agente hermano mínimo, p. ej. `GuionAgent`, si encaja mejor en el pipeline):
   - Si el lote trae `guion` → normalizar y guardar copia en `data/{slug}/pdf/{slug}_guion.md` y/o `meta/guion.json`
   - Si NO trae `guion` pero sí `temas` (+ contexto del lote) → **generar guion** (heurística MVP como `EscenasAgent._split_guion`, o plantilla por tema; LLM real queda para V1)
   - El guion debe poder alimentar `EscenasAgent` sin duplicar lógica innecesaria

2. **Contrato de salida** (ejemplo):
   ```json
   {
     "guion": "texto plano con escenas separadas por doble salto de línea",
     "escenas_preview": [{"id": 1, "titulo": "...", "texto_guion": "..."}],
     "archivo_md": "data/{slug}/pdf/{slug}_guion.md",
     "generado_desde": "temas|guion_existente"
   }
   ```

3. **Integración pipeline** (`src/pipeline.py`):
   - Si salida incluye `pdf` y se generó guion → escribir también en `lote` en memoria o en meta para que, si luego corre `video`, `EscenasAgent` lo use
   - Opcional: flag en lote `"pdf": {"generar_guion": true}` (default true cuando hay temas y no hay guion)

4. **Documentar** en `pdf/README.md` y `PROYECTO.md` (quitar de Pendiente V1 al terminar)

## Restricciones

- MVP local, sin APIs de pago
- No romper PDF actual ni flujo video existente
- Reutilizar convenciones: `save_json`, `AgentResult`, paths en `build_context`
- Cambio mínimo: preferir extender `PdfModule` o un agente pequeño antes que refactor grande
- Idioma del guion: español salvo que `lote.json` indique otro

## Archivos probables

- `pdf/agent.py`
- `src/pipeline.py`
- `src/agents/escenas_agent.py` (solo si hace falta factorizar `_split_guion` / `_build_escena`)
- `pdf/README.md`, `PROYECTO.md`
- Demo: `data/demo_pdf_guion/inputs/lote.json` con `"salidas": ["png", "pdf"]` y temas sin guion

## Criterios de éxito

- [ ] Correr pipeline con salida `pdf` y temas sin `guion` → produce `.pdf` **y** guion en `pdf/` o `meta/`
- [ ] Correr después con `"salidas": ["video"]` y `"video": {"modo": "animado"}` usando el guion generado → `escenas.json` válido
- [ ] Si el lote ya trae `guion`, no lo sobrescribe; solo lo exporta/normaliza junto al PDF
- [ ] QC y packager siguen pasando

Entrega: implementación + ejemplo de lote + notas breves de uso en README.
```

# Prompt — Mejorar Creador de Contenido (sin tocar otros proyectos)

- **Slug:** `mejorar-creador-contenido`
- **Proyecto:** solo `creador de contenido/`
- **Modo:** crear-pipeline Modo B (mejorar existente)

---

## Copia y pega esto en un chat nuevo de Cursor

```
Actúa como agente del proyecto **Creador de Contenido** únicamente.

## Frontera (obligatoria — no negociable)

1. Solo editas archivos dentro de:
   `creador de contenido/`
2. PROHIBIDO modificar:
   - `libros a entender/` (código, PDF, resumenes)
   - `tiktok_pipeline/`
   - `proyecto landing/`, `sitio-pdf/`, `linkedin-ghostwriter/`
   - skills/catálogos de otros proyectos
3. Lectura permitida (solo lectura) de rutas tipo `fuente_guia` hacia resúmenes ya generados.
4. Si hace falta registrar el CLI en `AGENTS.md` o `meta/router.json`, hazlo al FINAL y en 1–2 líneas, sin cambiar rutas de otros productos.
5. Diff mínimo. Un paso por vez. No refactor grande “por limpieza”.

## Estado actual (no reinventar)

- CLI: `creador_imagenes_main.py`
- Orquestador: `src/pipeline.py` + recetas `src/recipes.py` / `meta/recetas.json`
- Agentes: context, planner, hook, guion, escenas, style, prompt, captions, thumbnail, qc, packager
- Módulos: imagenes/, gifs/, videos/, pdf/
- Mock OK: MOCK_GENERATE=true, MOCK_KLING=true
- Demos: demo_lote, demo_animado, demo_promo_guia, demo_slideshow, demo_full

## Deudas conocidas (priorizar en este orden)

| # | Severidad | Deuda |
|---|-----------|--------|
| A | mejora | GenerateAgent muerto + plan.json desactualizado vs plan_runtime |
| B | mejora | Checkpoint escribe pero NO reanuda |
| C | mejora | Hook/guion/escenas son heurística; opcional LLM sin romper mock |
| D | crítico V1 | Imágenes reales (MOCK_GENERATE=false) sin romper placeholder |
| E | crítico V1 | Kling real (Kie + URLs públicas) con fallback a mock |

## Cómo trabajar (pasos)

### Paso 0 — Baseline (sin código de negocio)
1. Lee: PROYECTO.md, meta/constitution.json, meta/recetas.json, src/pipeline.py, logs/errores.json
2. Corre y anota PASS/FAIL:
   ```bash
   cd "creador de contenido"
   python3 creador_imagenes_main.py --slug demo_lote --modo png --reset-checkpoint
   python3 creador_imagenes_main.py --slug demo_promo_guia --receta promo-guia --reset-checkpoint
   ```
3. Escribe en chat un diagnóstico 🔴/🟡/🟢 (máx. 8 bullets). Espera OK antes de editar.

### Paso A — Limpieza segura (🟡)
- Eliminar o cablear `src/agents/generate_agent.py` (si no se usa: marcar deprecated o borrar solo si nada lo importa)
- Sincronizar `meta/plan.json` con agentes reales del pipeline (docs = runtime)
- Limpiar entrada stale de `logs/errores.json` solo si confirmas que ya no aplica
- Probar de nuevo demo_lote
- Actualizar `PROYECTO.md` checklist: A hecho

### Paso B — Checkpoint que reanuda (🟡)
- En `src/checkpoint.py` + `src/pipeline.py`: si hay `.checkpoint.json` y NO hay `--reset-checkpoint`, saltar pasos ya completados del plan_runtime
- CLI ya tiene `--reset-checkpoint`; no inventar flags nuevos salvo `--desde` si encaja con el patrón de tiktok_pipeline (copiar idea, no código cruzado)
- Prueba: correr promo-guia, matar a mitad (o simular last_completed), reanudar sin reset → no regenera PNG ya hechos
- Criterio: resume real, no solo historial

### Paso C — Copy con LLM opcional (🟡)
- Mantener mock/heurística si no hay API key
- Si `ANTHROPIC_API_KEY` (o la que ya uses en el repo) y flag tipo `MOCK_LLM=false`: HookAgent / GuionAgent / EscenasAgent pueden llamar LLM
- Cada agente sigue leyendo reglas locales (o skill md si añades `src/skills/` DENTRO de este proyecto)
- No dependas de instalar skills en `~/.cursor/skills`
- Probar con MOCK y con 1 llamada real limitada (`limit_escenas: 1`)

### Paso D — Imágenes reales detrás de flag (🔴 V1)
- `ImagenesModule` debe respetar `MOCK_GENERATE`:
  - true → placeholder actual
  - false → backend real (Replicate/Flux u otro ya documentado en .env.example)
- Si falla API → fallback a placeholder + warning en QC, no tumbar todo el lote
- Actualizar `.env.example` con vars reales
- Probar 1 PNG real + resto mock si hay cuota

### Paso E — Video Kling real detrás de flag (🔴 V1)
- En `src/video_backend.py`: si `MOCK_KLING=false` + `KIE_API_KEY` + URLs públicas de frames → clip real
- Si falta Cloudinary/URL pública → error claro + fallback mock (no romper demo)
- Probar `limit_escenas: 1` antes de lotes
- Documentar costo aproximado en PROYECTO.md sin inventar métricas

### Cierre de cada paso
1. Diff mínimo listado por archivo
2. Comando de prueba ejecutado
3. Actualizar `PROYECTO.md` (Pendiente V1 → hecho/parcial)
4. Append en `logs/mejoras.json`: `{paso, cambio, at}`
5. NO pases al siguiente paso sin que yo diga «sigue» / «paso X»

## Definition of Done global
- [ ] Demos mock siguen PASS
- [ ] Checkpoint reanuda
- [ ] plan.json = runtime
- [ ] MOCK_* flags de verdad cambian comportamiento
- [ ] Cero cambios en libros a entender / tiktok_pipeline / landing

## Empieza ahora
Ejecuta **solo Paso 0**. No edites código todavía. Devuélveme el diagnóstico.
```

---

## Mejora activa (v2) — Formato enseñanza

El video **no vende** por defecto: entrega una **enseñanza** del resumen (ej. Pareto), tono faceless educativo (ref. [Psicología Invisible](https://youtube.com/@lapsicologiainvisible)).

| Campo | Valor |
|-------|--------|
| Receta | `ensenanza` |
| Formato | `ensenanza` (vs `promo`) |
| Fuente | `fuente_guia` → resumen `.md` (solo lectura) |
| Guion | hook → concepto → por qué importa → 2 enseñanzas → aplicación → cierre suave |
| Prohibido en copy | “Comenta X”, hard sell, “descarga gratis” como mensaje central |

```bash
cd "creador de contenido"
python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza --reset-checkpoint
```

Demo: `data/video_pareto_psico/videos/video_pareto_psico.mp4`

---

## Mejora activa (v4) — Voz + letras limpias

1. **Duración:** Morph estira `hold_frames` para igualar `copy/narracion.mp3` (no cortar la voz con `-shortest` sobre un morph de ~8s).
2. **Subtítulos UX (obligatorio):**
   - Solo las **palabras** en pantalla (sin caja negra, sin sombra negra).
   - Aparecen **con la voz** y **desaparecen** (chunks cortos / fad in-out).
   - Formato ASS preferido; SRT solo como respaldo.
3. Receta: `ensenanza-tiktok`.

```bash
cd "creador de contenido"
python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza-tiktok --reset-checkpoint
```

---

## Cómo usarlo

1. Abre un chat nuevo con el workspace `cursorprime`.
2. Pega el bloque de arriba.
3. Di `sigue` / `paso A` / `paso B`… cuando quieras avanzar.
4. Si el agente propone tocar otro proyecto → recuérdale la frontera.
5. Para videos didácticos: usa receta `ensenanza`, no `promo-guia`.

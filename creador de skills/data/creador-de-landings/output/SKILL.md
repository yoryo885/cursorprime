---
name: creador-de-landings
description: >-
  Genera landings HTML en segundos: empieza con preguntas de brief, propone
  3 estilos (editorial, mockup, oferta) y construye preview.html. Usar cuando
  el usuario pide crear landing, generador de landings, landing en segundos,
  entrevista landing, usa creador-de-landings.
---

# Creador de Landings

## Cuándo usar

Triggers: crear landing, generador landings, landing en segundos, entrevista landing, usa creador-de-landings.

**Distinto de** `landing-lanzamiento` (solo copy markdown). Este proyecto **genera HTML**.

## Flujo

1. Entrevista (`meta/preguntas.json`)
2. 3 ejemplos de estilo → usuario elige
3. Brief + HTML (`preview.html`) + QC

## Comandos

```bash
cd creador-de-landings
python3 landings_main.py demo
python3 landings_main.py entrevista --slug mi-marca
python3 landings_main.py generar --slug mi-marca --ejemplo editorial
```

## Salida

`data/{slug}/output/preview.html` · `ejemplos.md` · `brief.md`

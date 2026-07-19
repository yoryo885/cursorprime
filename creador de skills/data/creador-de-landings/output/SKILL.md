---
name: creador-de-landings
description: >-
  Genera landings HTML en segundos: entrevista de brief, propone estilos
  (editorial, tienda tipo Filjós, mockup, oferta) y construye preview.html
  multiproducto. Usar cuando pide crear landing, generador de landings,
  landing en segundos, tienda/colección, filjos, usa creador-de-landings.
---

# Creador de Landings

## Cuándo usar

Triggers: crear landing, generador landings, landing en segundos, tienda, filjos, entrevista landing, usa creador-de-landings.

**Distinto de** `landing-lanzamiento` (solo copy markdown). Este proyecto **genera HTML**.

## Flujo

1. Entrevista (`meta/preguntas.json`)
2. Estilos → usuario elige (`editorial` | `tienda` | `mockup` | `oferta`)
3. Brief + HTML (`preview.html`) + QC

Estilo **tienda** = look colección ecommerce (estructura tipo [filjos.com](https://filjos.com/)). Ver `creador-de-landings/meta/referencias/filjos.md`.

## Comandos

```bash
cd creador-de-landings
python3 landings_main.py demo --ejemplo tienda
python3 landings_main.py entrevista --slug mi-marca
python3 landings_main.py generar --slug mi-marca --ejemplo tienda
python3 landings_main.py aprender --mensaje "..." --cambio "..."
```

La landing ofrece **catálogo** (varias guías libro×rol), no un solo PDF.

## Salida

`data/{slug}/output/preview.html` · `ejemplos.md` · `brief.md`

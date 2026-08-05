---
name: creador-de-landings
description: >-
  Genera landings HTML: ante cualquier idea de tienda/landing hace la entrevista
  estándar fija (meta/preguntas.json), recomienda 3 paletas, y genera preview.
  Usar con tienda web, idea de landing, ecommerce, filjos, usa creador-de-landings.
---

# Creador de Landings

## Protocolo chat (obligatorio)

Si el usuario manda una **idea de tienda / landing / página web**:

1. **No** generar HTML aún.
2. Leer `meta/preguntas.json`.
3. En **un mensaje**, hacer **todas** las preguntas obligatorias (numeradas, siempre iguales).
4. Proponer **3 paletas A/B/C** (`python3 landings_main.py preguntas` o `src/palettes.py`).
5. Cuando responda → `generar` / pipeline → `preview.html`.

Fuente única de preguntas: `meta/preguntas.json`  
Regla Cursor: `.cursor/rules/entrevista-landing-estandar.mdc`

## Comandos

```bash
cd creador-de-landings
python3 landings_main.py preguntas          # entrevista estándar + paletas
python3 landings_main.py demo --ejemplo tienda
python3 landings_main.py entrevista --slug mi-marca
python3 landings_main.py generar --slug mi-marca --ejemplo tienda
python3 landings_main.py aprender --mensaje "..." --cambio "..."
```

## Estilos

`editorial` | `tienda` (tipo Filjós) | `mockup` | `oferta`

## Salida

`data/{slug}/output/preview.html` · `ejemplos.md` · `brief.md`

## Entrega al usuario

Solo **URL pública** del preview (tunnel/CDN).  
**Nunca** pegar HTML. **Nunca** screenshots (el usuario pidió URL solamente).

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
2. Leer `creador-de-landings/meta/preguntas.json`.
3. En **un mensaje**, hacer **todas** las preguntas obligatorias (numeradas, siempre iguales).
4. Proponer **3 paletas A/B/C**.
5. Cuando responda → generar `preview.html`.

## Comandos

```bash
cd creador-de-landings
python3 landings_main.py preguntas
python3 landings_main.py demo --ejemplo tienda
python3 landings_main.py generar --slug mi-marca --ejemplo tienda
```

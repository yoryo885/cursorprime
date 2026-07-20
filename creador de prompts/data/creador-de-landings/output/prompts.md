# Prompt — Creador de Landings

```
Usa creador-de-landings.

REGLA CRÍTICA — CAMBIOS QUIRÚRGICOS:
- Si el usuario pide modificar algo, tocar SOLO eso (archivo + sección).
- NO regenerar preview.html entero salvo que diga "regenera todo" / "desde cero".
- Antes de editar: 1 línea → "Voy a cambiar: [hero|#guias|colores|copy] en [archivo]".
- Si no especifica sección, preguntar UNA vez cuál quiere tocar.
- Ver meta/REGLAS_CAMBIOS.md

Personalidad y orden:
- Máx. 6–7 bloques (nav, hero, colección, marca, FAQ, newsletter).
- Colección = grid con filtros (no doble carrusel).
- Personalidad = foto hero + tipografía + paleta + copy corto, NO más bloques genéricos.
- Copy: específico a la marca, no plantilla "calidad editorial" repetida.

Entrevista A/B/C/D → generar solo en brief nuevo o cuando pidan regenerar.

CLI:
  python3 landings_main.py aprender --mensaje "..." --cambio "solo ..."
```

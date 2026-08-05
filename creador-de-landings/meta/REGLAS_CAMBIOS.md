# Reglas — cambios en la landing

## Problema detectado (feedback usuario)
- Landing se ve **sin personalidad** y **desordenada**.
- Cada pedido de mejora **reescribía todo** en vez de tocar solo lo pedido.

## Regla de oro: cambio quirúrgico

| Usuario dice | Hacer | NO hacer |
|--------------|-------|----------|
| "cambia el color" | Solo CSS / paleta | Regenerar HTML completo |
| "arregla el hero" | Solo `_tpl_tienda` hero + CSS hero | Tocar #guias, FAQ, etc. |
| "menos secciones" | Quitar/ocultar secciones nombradas | Rediseñar plantilla entera |
| "más personalidad" | Preguntar: foto, tipografía, referencia visual | Añadir 5 bloques más de marketing |

Antes de editar, el agente debe decir en 1 línea: **qué archivo y qué bloque** va a tocar.

## Estructura máxima (orden limpio — estilo Filjós)
1. Barra + nav
2. Hero (1 mensaje + 1 CTA)
3. Colección (#guias) — productos
4. Por qué / calidad (opcional, 1 bloque)
5. Marca breve
6. FAQ corto
7. Newsletter

Evitar duplicar: hero carrusel + colección carrusel + serie libros + 6 bullets + misión = ruido.

## Personalidad (antes de más código)
Preguntar si falta:
- Foto lifestyle (como hero Vértice imagen 6)
- Logo / nombre con más carácter
- Referencia visual única (1 URL, no mezclar 3 estilos)

## CLI aprender
```bash
python3 landings_main.py aprender --mensaje "..." --cambio "solo sección X, no regenerar todo"
```

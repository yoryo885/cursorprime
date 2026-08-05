# Referencia — Filjós (filjos.com)

Idea de página tipo **tienda / marca** que el sistema puede generar con el estilo `tienda`.

Fuente: https://filjos.com/ (joyería islandesa). No copiar marca ni textos; sí la **estructura**.

## Bloques que venden (patrón)

| Bloque | Qué hace | En nuestro sistema |
|--------|----------|--------------------|
| Barra superior | Descuento newsletter + envío + Trustpilot | `barra_aviso` + prueba social genérica |
| Nav por colección | Sets, collares, aros… | Filtros por **rol** / libro |
| Hero “Ahora nuevo” | Lanza producto estrella + CTA | Primera guía `disponible` |
| Bestsellers | Grid con precio + add to cart | Catálogo multi-producto |
| Shop the Look | Look combinado (varios SKUs) | Sets / packs (opcional) |
| Historia de marca | Quiénes son + inspiración | `historia` / promesa de marca |
| Sets populares | Bundles con precio tachado | Packs libro×rol (futuro) |
| Testimonios | Prueba social real | Solo reales o `[PENDIENTE]` |
| Causa / misión | 10% a causas | Opcional (`mision`) |
| Newsletter | Captura email + 10% | CTA secundario |

## Por qué encaja con Vértice Pro

- No vende un solo SKU: vende **colección**.
- Filtros por categoría = filtros por **rol**.
- Hero de marca + grid abajo (como ya pedimos multiproducto).
- Bundles = packs de guías más adelante.

## Uso

```bash
python3 landings_main.py generar --slug demo-cliente --ejemplo tienda
# o
python3 landings_main.py demo --ejemplo tienda
```

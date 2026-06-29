# Operador de pipeline

Orquestador del **Creador de Contenido**. No es un módulo de salida (PNG/GIF/MP4).

## Dónde está el código

| Pieza | Ruta |
|-------|------|
| Orquestador | `src/pipeline.py` |
| Core (context, style, prompt, qc, packager) | `src/agents/` |
| CLI | `creador_imagenes_main.py` |

## Módulos de salida (carpetas reales en la raíz)

| Carpeta | Qué genera |
|---------|------------|
| `imagenes/` | PNG |
| `gifs/` | GIF |
| `videos/` | MP4 |
| `pdf/` | PDF |

Los archivos generados van en `data/{slug}/imagenes/`, etc.

## Comando

```bash
python3 creador_imagenes_main.py --slug demo_lote --modo all
```

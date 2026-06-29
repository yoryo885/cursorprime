# Módulo Video

Dos modos en `lote.json` → `video.modo`:

## slideshow (actual / MVP gratis)
PNG₁ + PNG₂ + PNG₃ → ffmpeg → 1 MP4  
Ideal: previews, borradores.

```json
"video": { "modo": "slideshow", "fps": 2 }
```

## animado (estilo video YouTube)
Guion → escenas → frame INICIO + FIN → clip por escena → MP4 final  
Con `MOCK_KLING=true`: crossfade local (sin API).  
Con `KIE_API_KEY`: Kling real (pendiente Cloudinary).

```json
"video": { "modo": "animado", "limit_escenas": 2 },
"guion": "Párrafo 1...\n\nPárrafo 2..."
```

Salida:
```
data/{slug}/videos/clips/01-*.mp4
data/{slug}/videos/{slug}.mp4
```

Agente: `VideosModule` en `agent.py`

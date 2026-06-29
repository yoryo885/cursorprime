# Creador de Contenido

Proyecto **independiente** en `~/cursorprime/creador de contenido`.

Genera **PNG · GIF · Video · PDF** — cada modo solo o combinado. Sin conexión a otros proyectos (hooks listos para futuro).

## Comandos

```bash
cd "/Users/yoryo/cursorprime/creador de contenido"
pip install -r requirements.txt

# Solo imágenes
python creador_imagenes_main.py --slug demo_lote --modo png

# Solo GIF
python creador_imagenes_main.py --modo gif --slug demo_full

# PNG + GIF + PDF
python creador_imagenes_main.py --slug demo_full --modo all

# Video (requiere: brew install ffmpeg)
python creador_imagenes_main.py --modo video --slug demo_slideshow

# Video ANIMADO (guion → escenas → clips)
python creador_imagenes_main.py --modo video --slug demo_animado
```

## Arquitectura

```
imagenes/        → módulo PNG
gifs/            → módulo GIF (frames)
videos/          → módulo MP4 (usa PNG)
pdf/             → módulo PDF (usa PNG)
src/agents/      → core: context, style, prompt, qc, packager
src/pipeline.py  → orquestador
```

## Entrada lote.json

```json
{
  "titulo": "Mi pack",
  "salidas": ["png", "gif"],
  "temas": ["enfoque", "tiempo"],
  "gif": {"frames": 4}
}
```

## Salida

```
data/{slug}/
├── imagenes/
├── gifs/
├── videos/
├── pdf/
└── output/{slug}_contenido.zip
```

## Video — dos modos

| Modo | Qué hace | Costo |
|------|----------|-------|
| `slideshow` | PNGs → ffmpeg concat | Gratis |
| `animado` | Guion → escenas → frame A+B → clip/escena → MP4 | Mock gratis / Kling ~$0.40/escena |

```json
{
  "video": { "modo": "animado", "limit_escenas": 2 },
  "guion": "Texto del video...\n\nOtra escena..."
}
```

## Pendiente V1

- **PDF + guiones de video** — el módulo PDF no debe limitarse al documento; también debe poder generar guiones para video (prompt activo: `data/pdf-guion-video/output/`)
- IA real imágenes (Replicate/Flux) — `MOCK_GENERATE=false`
- Kling real (Kie.ai + Cloudinary URLs) — `MOCK_KLING=false` + `KIE_API_KEY`
- Conexión creador de prompts (elegir pack al iniciar)
- Integración externa — `INTEGRACION_EXTERNA=true`

## Del video YouTube — qué falta rescatar

| Del video | Estado |
|-----------|--------|
| Guion → escenas | ✅ EscenasAgent |
| Frame inicio + fin | ✅ modo animado |
| Biblioteca estilos | ✅ meta/estilos_animacion.json |
| Clips ordenados + MP4 final | ✅ videos/clips/ |
| Slideshow simple | ✅ modo slideshow |
| OpenAI divide guion (LLM) | ⏳ hoy heurística; Cursor chat o API |
| Gemini genera frames | ⏳ mock Pillow; API V1 |
| Kling image-to-video | ⏳ mock ffmpeg; Kie pendiente |
| Cloudinary URLs | ⏳ solo si API lo exige |
| n8n / Baserow / webhooks | ❌ no necesario (pipeline Python) |
| Google Drive auto-upload | ⏳ opcional futuro |
| UI “Activar” en tabla | ⏳ CLI por ahora |
| Costos por escena | ⏳ logs futuro |

---
name: guion-a-video
description: >-
  Sistema de creación de videos en creador de contenido: planner + agentes/skills
  condicionales según receta (slideshow, animado, promo-guia, reels-pack). Usar
  cuando el usuario menciona guion a video, promo de guía PDF, sistema de video,
  receta promo-guia, modo animado, usa guion-a-video, o pide pipeline de video.
---

# Guion a Video (sistema por recetas)

Skill de **workflow** para Creador de Contenido.

## Cuándo usar

Activar cuando el usuario diga: guion a video, crear video, promo guía PDF, sistema de video, receta, modo animado, reels pack, usa guion-a-video.

## Idea clave

No corren todos los agentes siempre. El **PlannerAgent** lee la **receta** del lote y activa solo lo necesario:

| Receta | Para qué |
|--------|----------|
| `slideshow` | Preview PNG→MP4 |
| `animado` | Guion → escenas → clips |
| `promo-guia` | Promocionar PDF/guía (hook+guion+video+captions+thumb) |
| `reels-pack` | Pack redes completo |
| `custom` | Según `salidas` / `copy` del lote |

## Skills embebidas como agentes

| Skill chat | Agente pipeline |
|------------|-----------------|
| hooks-redes | HookAgent |
| guion-a-video | GuionAgent + EscenasAgent + VideosModule |
| captions-redes | CaptionsAgent |
| thumbnail-social | ThumbnailAgent |

## Pasos

1. **Definir necesidad**: ¿promo de guía, animado, slideshow, pack redes?
2. **Armar lote.json** con `receta` (o dejar que infiera: si hay `guia` → `promo-guia`).
3. **Ejecutar**:
   ```bash
   cd "creador de contenido"
   python3 creador_imagenes_main.py --listar-recetas
   python3 creador_imagenes_main.py --slug {slug} --receta promo-guia --reset-checkpoint
   ```
4. **Entregar**: `data/{slug}/videos/`, `copy/`, `meta/plan_runtime.json`, zip en `output/`.

## Reglas

- Probar con `limit_escenas: 1` o `2` y `MOCK_KLING=true`.
- No inventar métricas; copy heurístico lleva `confidence` medium/low.
- Ruta: `creador de contenido/`.

## Proyecto

Carpeta: `../creador de contenido`

# Prompts — Sistema de video por recetas (promo guías PDF)

- **Tipo:** animacion / cursor
- **Proyecto:** creador-de-contenido
- **Slug:** pdf-guion-video
- **Estado:** activo (mejora continua)

## Objetivo actual

Usar `creador de contenido` como **sistema de creación de videos** con agentes y skills que se activan según la necesidad del video (promo de guías PDF, animado, slideshow, pack redes), orquestado como pipeline con Planner.

## Prompt operativo (copiar)

```
Actúa sobre el proyecto **Creador de Contenido**.

Sistema de video por recetas (`meta/recetas.json` + `PlannerAgent`):

1. Elegir receta según necesidad:
   - promo-guia → promocionar guía/PDF (hook→guion→escenas→video→captions→thumbnail)
   - animado → guion ya escrito
   - slideshow → preview rápido
   - reels-pack → pack redes completo

2. Entrada mínima promo-guia en data/{slug}/inputs/lote.json:
   - guia.titulo, guia.promesa, guia.ideas[], guia.cta
   - opcional fuente_guia → resumen.md de libros a entender
   - video.limit_escenas (probar con 2)

3. Correr:
   python3 creador_imagenes_main.py --slug {slug} --receta promo-guia --reset-checkpoint

4. Entregar: videos/*.mp4, copy/, meta/plan_runtime.json (skills/agentes activados), zip.

Reglas: MOCK_KLING=true en pruebas; no inventar métricas; confidence bajo en copy heurístico.
```

## Mejoras integradas

1. Pipeline con agentes condicionales (no todo corre siempre).
2. Skills hooks-redes / guion-a-video / captions-redes / thumbnail-social embebidas como agentes.
3. Receta `promo-guia` para videos que promocionan guías de PDFs creados.
4. Demo: `data/demo_promo_guia/`.

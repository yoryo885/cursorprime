---
name: guion-a-video
description: >-
  Convierte un guion de video en escenas con frames inicio/fin y clips animados
  usando el pipeline de creador de contenido. Conecta con creador de prompts si
  hace falta prompts exactos por escena. Proyecto: Creador de Contenido. Usar
  cuando el usuario menciona guion a video, crear video desde guion, modo
  animado, escenas de video, usa guion-a-video, o pide seguir este flujo paso a paso.
---

# Guion a Video

Skill de **workflow** para Creador de Contenido.

## Cuándo usar

Activar cuando el usuario diga: guion a video, crear video desde guion, modo animado, escenas de video, usa guion-a-video.

## Proceso

Convierte un guion de video en escenas con frames inicio/fin y clips animados usando el pipeline de creador de contenido. Conecta con creador de prompts si hace falta prompts exactos por escena.

## Pasos

1. **Recibir guion**: Texto libre o archivo. Confirmar titulo del video y estilo (meta/estilos_animacion.json).
2. **Generar prompts (opcional)**: Si no hay pack: correr creador de prompts tipo animacion → proyecto creador-de-contenido.
3. **Armar lote.json**: salidas: [png, video], video.modo: animado|slideshow, guion, limit_escenas para pruebas.
4. **Ejecutar pipeline**: cd cursorprime/creador de contenido && python3 creador_imagenes_main.py --slug {slug} --modo video
5. **Entregar**: data/{slug}/videos/clips/ + MP4 final + manifest. Indicar si MOCK_KLING o Kling real.

## Reglas

- Modo slideshow = gratis (ffmpeg). Modo animado = frame A+B (mock o Kling).
- Probar con limit_escenas: 1 antes de lote completo.
- No inventar metricas; el guion define las escenas.
- Ruta base: ~/cursorprime/creador de contenido

## Proyecto

Carpeta: `../creador de contenido`

## Iteración

Si el resultado no encaja, pedir feedback y actualizar esta skill (v2 en misma carpeta).

# Agentes + skills — video enseñanza TikTok (capítulo ancla)

Objetivo: el video estilo Psicología Invisible (personaje + escenas + voz + letras) se crea **solo con agentes/skills**, no a mano.

## Cadena (receta `ensenanza-tiktok`)

| Orden | Agente | Skill | Entrega |
|------:|--------|-------|---------|
| 1 | Context | — | lote + paths |
| 2 | Planner | — | plan_runtime (qué corre) |
| 3 | Hook | hooks-redes | gancho 1 frase |
| 4 | Guion | guion-a-video | guion didáctico (beats) |
| 5 | Escenas | guion-a-video | beats → escenas A/B |
| 6 | Style | — | estilo blob / faceless |
| 7 | Prompt | — | prompts por escena (personaje fijo) |
| 8 | PNG | — | frames inicio/fin (o mock) |
| 9 | **Morph** | guion-a-video / morph-escenas | morph A→B + concat = video base |
| 10 | Audio | audio-redes + ElevenLabs | narracion.mp3 + mux |
| 11 | **Subtitulos** | subtitulos-burn | `.srt` + video con letras (lo que dice la voz) |
| 12 | Captions | captions-redes | copy redes |
| 13 | Thumbnail | thumbnail-social | portada |
| 14 | QC | — | valida |
| 15 | Packager | — | zip |

## Lo que faltaba (ahora agentes)

1. **MorphAgent** — empaqueta las 5 escenas con animación fluida (antes era script manual).
2. **SubtitulosAgent** — pone en pantalla lo que dice la voz (SRT + burn-in ffmpeg).

## Mejoras que van de la mano

| Mejora | Dónde vive |
|--------|------------|
| Duración voz ↔ imagen | Morph hold por beat + Audio; Subtitulos usa duración real del audio |
| Capítulo ancla + cortes | mismo máster; Packager/futuro `cortes` agent |
| Estilo blob | Style + Prompt (formato ensenanza) |
| Sin hard sell | Guion/Hook formato ensenanza |
| Texto on-screen | **SubtitulosAgent** |

## Cómo correr

```bash
cd "creador de contenido"
python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza-tiktok --reset-checkpoint
```

Si ya tienes stills en `refs/escenas/*_a.png` / `*_b.png`, Morph las usa primero.

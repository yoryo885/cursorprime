# Plantilla: escenas + animación fluida (interacción)

Flujo estilo Psicología Invisible / personaje blob:

1. **Imagen base** del personaje (misma cara/cuerpo).
2. **Escenarios** distintos (acción + lugar + banner).
3. **Pose B** por escenario: el personaje **interactúa con objetos** (no solo gesticula en el aire).
4. **Morph ping-pong** A↔B + idle, sync a `narracion.mp3`.

## Pack actual

| # | Stem | Interacción |
|---|------|-------------|
| 01 | abrumado | señala papeles ↔ manos a la cabeza |
| 02 | diagrama | señala el 20% del gráfico |
| 03 | piedras | mira lo pequeño ↔ prioriza |
| 04 | lista | marca prioridades |
| 05 | claridad | cierre / ventana |
| 06 | tachar | **señala ítem ↔ tacha lo secundario** |
| 07 | piedra_vital | **toca piedrita ↔ abraza piedra grande** |
| 08 | protege_tiempo | **mira agenda ↔ protege bloque de tiempo** |

```bash
python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza-tiktok --desde morph
```

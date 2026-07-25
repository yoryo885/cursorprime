# Plantilla: 5 escenas + animación fluida

Flujo que funcionó (estilo Psicología Invisible / personaje blob):

1. **Imagen base** del personaje (misma cara/cuerpo).
2. **5 escenarios** distintos (acción + lugar + banner).
3. **Pose B** por cada escenario (mismo fondo, solo cambia gesto).
4. **Morph fluido** pose A→B (~1.5–2 s) y concat de las 5.

```bash
# entregable
videos/pareto_5_escenas_animado.mp4   # historia completa ~8s
videos/clips_escenas/01_….mp4        # clip por escena
refs/escenas/*_a.png / *_b.png       # stills
```

Para otro tema: mismas 4 pasos, cambias banners y acciones del lote.

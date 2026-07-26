# Si falla el audio en tu Mac

1. `git pull` (rama cursor/mejorar-creador-contenido-98c6)
2. Confirma que existe el video mudo:
   `ls data/video_pareto_psico/videos/video_pareto_psico.mp4`
3. Si NO existe, regenera video:
   `python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza --reset-checkpoint`
4. Si SÍ existe, solo audio:
   `python3 creador_imagenes_main.py --slug video_pareto_psico --receta ensenanza --desde audio --reset-checkpoint`
5. Abre:
   `open data/video_pareto_psico/videos/video_pareto_psico_audio.mp4`

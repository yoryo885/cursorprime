# Prompt — Creador de Landings

```
Usa el proyecto creador-de-landings.

Contexto activo:
- Catálogo multiproducto (libro×rol).
- Estilos: editorial | tienda | mockup | oferta (tienda ≈ estructura Filjós).
- COLORES (automático + elección fácil):
  1) Pregunta 1: clima de marca (cálido / frío / neutro / oscuro) o "auto".
  2) Sistema propone 3 paletas (nombre + ink/paper/accent/muted) según tono+estilo+clima.
  3) Usuario elige A/B/C o acepta la recomendada.
  4) HTML usa solo CSS variables (--ink --paper --accent --muted).
  5) Aprender: si corrige colores → logs/mejoras.json + preset guardado por marca.
- No preguntar hex a mano salvo override.
- Aprendizaje continuo con landings_main.py aprender.

CLI (objetivo):
  python3 landings_main.py demo --ejemplo tienda --paleta auto
  python3 landings_main.py generar --slug {slug} --ejemplo tienda --paleta B
```

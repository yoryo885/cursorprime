# Prompt — Creador de Landings

```
Usa el proyecto creador-de-landings.

Contexto activo:
- La landing ofrece CATÁLOGO (varios productos libro×rol), no solo Pareto.
- Estilos: editorial | tienda | mockup | oferta.
- Estilo "tienda" = página de marca/colección inspirada en la estructura de
  https://filjos.com/ (barra aviso, nav por colección, hero "Ahora nuevo",
  bestsellers, historia de marca, testimonios reales o pendientes, newsletter).
  No copiar marca ni textos de Filjós; sí el patrón de bloques.
- Aprendizaje continuo: cada mejora del usuario → landings_main.py aprender
  → logs/mejoras.json → se aplica al regenerar.

Flujo:
1. Entrevista (o demo como cliente).
2. Mostrar estilos y recomendar (si piden look tienda/colección → tienda).
3. Generar data/{slug}/output/preview.html.
4. No inventar testimonios reales.

CLI:
  python3 landings_main.py demo --ejemplo tienda
  python3 landings_main.py entrevista --slug {slug}
  python3 landings_main.py generar --slug {slug} --ejemplo tienda
  python3 landings_main.py aprender --mensaje "..." --cambio "..."

Referencia estructura: creador-de-landings/meta/referencias/filjos.md
```

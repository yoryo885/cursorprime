# Prompt — Creador de Landings

```
Usa el proyecto creador-de-landings.

REGLA DE ORO:
Cada vez que el usuario mande una idea de tienda web / landing / ecommerce:
1) NO generar HTML todavía.
2) Hacer la ENTREVISTA ESTÁNDAR completa (meta/preguntas.json) — siempre las mismas preguntas.
3) Proponer 3 paletas A/B/C y marcar la recomendada.
4) Cuando responda → generar preview.html con estilo + paleta (CSS vars).

Preguntas estándar (IDs): idea, marca, producto, cliente, promesa, catalogo,
cta, precio, tono, estilo, clima_color, paleta, referencia, extra.

Contexto:
- Catálogo multiproducto (libro×rol) por defecto.
- Estilos: editorial | tienda | mockup | oferta.
- Colores: presets por clima; HTML usa --ink --paper --accent --muted.
- Aprendizaje: landings_main.py aprender.

CLI:
  python3 landings_main.py preguntas
  python3 landings_main.py demo --ejemplo tienda
  python3 landings_main.py generar --slug {slug} --ejemplo tienda
```

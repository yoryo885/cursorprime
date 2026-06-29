# Lluvia de ideas

**Propuestas categorizadas con tu OK.** Lee análisis de `../analisis-de-proyectos/` — no investiga aquí.

## Flujo completo

```
analisis-de-proyectos  →  analizar / radar
        ↓
lluvia-de-ideas        →  lluvia / cola aprobar
        ↓
ideas de proyectos     →  evaluar / diseñar / construir
```

## Comandos (esta carpeta)

```bash
cd "/Users/yoryo/cursorprime/lluvia-de-ideas"

# Ideas desde análisis existente
python3 lluvia_main.py lluvia --desde-analisis demo_investigacion

# Todo: analizar (delega) + lluvia
python3 lluvia_main.py todo --texto "nicho kdp"

# Cola
python3 lluvia_main.py cola listar
python3 lluvia_main.py cola aprobar idea-xxx
python3 lluvia_main.py cola posponer idea-xxx
python3 lluvia_main.py pack-visual --desde-analisis demo_investigacion
```

Investigación y radar → ver **`../analisis-de-proyectos/PROYECTO.md`**

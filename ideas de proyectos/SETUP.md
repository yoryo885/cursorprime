# Setup — Ideas de proyectos

Meta-proyecto: **diseña primero, construye cuando tú digas que está listo**.

## Flujo en 2 fases

```
IDEA  →  diseñar  →  borradores/{slug}/   →  (tú revisas)  →  construir  →  proyectos/{slug}/
         pasos 1-4                              DISEÑO.md           pasos 5-7
```

## Cómo usar con New Agent

1. Abre en Cursor la carpeta **`ideas de proyectos`**
2. **New Agent** (⌘N)
3. Escribe tu idea o pide diseñar un JSON de `ideas/`

### Solo diseño (default)

> Diseña el proyecto desde ideas/ejemplo-idea.json

El agente escribe en `borradores/` y **no** toca `proyectos/`.

### Cuando estés listo

> **Construye dropship_ml — está listo**

Solo entonces crea el repo en `proyectos/`.

## CLI

```bash
cd "/Users/yoryo/cursorprime/ideas de proyectos"

python main.py diseñar ideas/ejemplo-idea.json
python main.py listar
python main.py construir dropship_ml    # solo cuando tú quieras
```

## Estructura

```
ideas de proyectos/
├── AGENTS.md              ← instrucciones para New Agent
├── main.py                ← CLI del meta-creador
├── ideas/                 ← tus ideas (JSON)
├── borradores/            ← diseño (brief, plan, DISEÑO.md)
├── proyectos/             ← repos construidos (vacío hasta "construir")
└── src/agents/            ← agentes del meta-creador
```

## Palabras que autorizan construcción

- `construye`
- `armado`
- `crea el proyecto`
- `construir {slug}`

Sin una de esas frases → **solo diseño**.

## No uses Skills

Todo vive en este proyecto. Abre esta carpeta y usa New Agent.

# Creador de Landings

Pipeline cursorprime: **entrevista → ejemplos → landing HTML** en segundos.

## Flujo

```mermaid
flowchart LR
  A[Interview] --> B[Examples]
  B --> C[Brief]
  C --> D[Build HTML]
  D --> E[QC]
  E --> F[Packager]
```

## CLI

```bash
cd creador-de-landings

# Demo como cliente (Vértice Pro — catálogo completo)
python3 landings_main.py demo

# Entrevista interactiva
python3 landings_main.py entrevista --slug mi-marca

# Generar (usa data/{slug}/inputs/catalogo.json si existe)
python3 landings_main.py generar --slug mi-marca --ejemplo editorial

# Registrar mejora (aprendizaje continuo)
python3 landings_main.py aprender --mensaje "..." --cambio "..."
```

## Catálogo (no solo Pareto)

- Default: `meta/catalogo_default.json` (libros × roles)
- Por marca: `data/{slug}/inputs/catalogo.json`
- La landing muestra **grid + filtros por rol** (disponibles y próximamente)

## Aprendizaje

Cada mejora del usuario → `logs/mejoras.json` → se reinyecta en el brief (`aprendizaje[]`).

## Entrada

- Preguntas en `meta/preguntas.json`
- Respuestas: `data/{slug}/inputs/respuestas.json`
- Estilo elegido: `ejemplo` = `editorial` | `mockup` | `oferta`

## Salida

```
data/{slug}/output/
├── preview.html      # landing lista
├── brief.md          # resumen del brief
├── ejemplos.md       # 3 estilos propuestos
└── manifest.json
```

## MVP / V1 / Futuro

| Fase | Qué |
|------|-----|
| **MVP** | Entrevista + 3 ejemplos + HTML estático (3 plantillas) + demo cliente |
| **V1** | Imagen hero IA / Unsplash, export Shopify sections, A/B headlines |
| **Futuro** | Multi-página, i18n, conectar creador de contenido para assets |

## Relación con otros proyectos

| Proyecto | Rol |
|----------|-----|
| `landing-lanzamiento` (skill) | Solo copy/brief markdown |
| **creador-de-landings** | Genera HTML real |
| `vertice-pro-preview` | Referencia visual (imagen 6 / hero) |
| `sitio-pdf` | Tienda PDF + Shopify zip |

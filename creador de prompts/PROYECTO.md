# Creador de Prompts

Servicio **compartido** para todos los proyectos de `cursorprime`.

Genera prompts listos para usar según **tipo** y **proyecto destino**.

## Comandos

```bash
cd "/Users/yoryo/cursorprime/creador de prompts"
pip install -r requirements.txt

# Demo
python3 creador_prompts_main.py --slug demo

# Por tipo y proyecto
python3 creador_prompts_main.py --tipo copy --proyecto libros-a-entender --slug kdp-pareto

# Desde solicitud custom
python3 creador_prompts_main.py --solicitud mi_solicitud.json --slug mi_lote
```

## Tipos disponibles

| Tipo | Uso |
|------|-----|
| `imagen` | Flux, Midjourney, DALL·E → **creador de contenido** |
| `copy` | Textos, posts, descripciones |
| `cursor` | Instrucciones para agentes Cursor |
| `pipeline` | Diseño de pipelines Python |
| `marketing` | KDP, Amazon, ads → **libros a entender** |
| `evaluacion` | Viabilidad de ideas → **ideas de proyectos** |

## Entrada `solicitud.json`

```json
{
  "titulo": "Mi pack",
  "tipo": "imagen",
  "proyecto_destino": "creador-de-contenido",
  "temas": ["enfoque", "tiempo"],
  "contexto": {
    "audiencia": "emprendedores",
    "tono": "claro",
    "estilo": "flat minimal"
  }
}
```

## Salida

```
data/{slug}/output/
├── prompts.json
├── prompts.md
└── manifest.json
```

## Proyectos registrados

Ver `meta/proyectos.json`. Al crear un proyecto nuevo, agrégalo ahí.

## Invocar desde Cursor

En **todo cursorprime**, cada mensaje **mejora el prompt activo** (regla `creador-prompts-siempre.mdc`). No acumula pendientes.

Estado del prompt activo: `meta/prompt-activo.json`

## Integración (futuro)

`INTEGRACION_EXTERNA=false` — otros proyectos leen `output/prompts.json` manualmente por ahora.

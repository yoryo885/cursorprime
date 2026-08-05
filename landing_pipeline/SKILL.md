# Skill: landing-pipeline

Pipeline de agentes (01–12) + skills `.md` por sección → landing HTML.

## Cuándo usarlo

- Pedido: "pipeline de landings", "agentes por sección", "skills hero/faq/pricing"
- Generar landing sección por sección con QA al final
- Distinto de `creador-de-landings` (entrevista A/B/C/D + plantillas tienda)

## CLI

```bash
cd landing_pipeline
python3 landing_main.py run --demo
python3 landing_main.py run --input meta/ejemplo-negocio.json --slug mi-marca
python3 landing_main.py run --slug vertice-pro --retry-from 07_pricing
python3 landing_main.py run --slug vertice-pro --solo 11_design
```

## Contrato

Cada agente: `def run(input: dict) -> dict`
Antes de generar: lee `src/skills/{seccion}_skill.md`.

## Outputs

`output/{slug}/brief.json`, `copy.json`, `landing.html`, `qa_report.json`

## LLM

Sin `ANTHROPIC_API_KEY` → mock (skills + brief). Con clave → Claude.

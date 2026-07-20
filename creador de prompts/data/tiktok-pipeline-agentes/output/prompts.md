# Prompts — Pipeline TikTok

- **Slug:** tiktok-pipeline-agentes
- **Proyecto:** tiktok_pipeline
- **Fuente:** prompt_pipeline_tiktok_7a6a.pdf

## Prompt operativo

```
Corre el pipeline TikTok:

cd tiktok_pipeline
MOCK_LLM=true python3 tiktok_main.py --tema "{TEMA}" --nicho "{NICHO}" --reset-checkpoint

Entrega: output/{slug}/shotlist.md (para grabar), guion.json, qa_report.json.
Cada agente debe haber leído su skill en src/skills/ antes de generar.
```

## Demo corrida

Tema: Principio de Pareto · slug: demo_pareto · QA score 100

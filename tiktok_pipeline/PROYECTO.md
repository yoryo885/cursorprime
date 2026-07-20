# TikTok Pipeline

Pipeline Python de agentes para crear guiones de TikTok listos para grabar.

Cada agente lee su **skill** (`.md` en `src/skills/`) antes de generar. Orquestación secuencial con checkpoint y outputs JSON + shotlist markdown.

## Comando

```bash
cd tiktok_pipeline
pip install -r requirements.txt
cp .env.example .env

# Mock (sin API)
MOCK_LLM=true python3 tiktok_main.py --tema "Principio de Pareto" --nicho "productividad" --reset-checkpoint

# Claude real
# MOCK_LLM=false ANTHROPIC_API_KEY=... python3 tiktok_main.py --tema "..." 
```

## Agentes

| # | Agente | Skill |
|---|--------|-------|
| 01 | trend_research | — |
| 02 | hook | hook_skill.md |
| 03 | script | script_skill.md |
| 04 | pattern_interrupts | pattern_interrupt_skill.md |
| 05 | onscreen_text | onscreen_text_skill.md |
| 06 | cta | cta_skill.md |
| 07 | loop | loop_skill.md |
| 08 | audio | audio_skill.md |
| 09 | caption_hashtags | caption_hashtags_skill.md |
| 10 | shotlist | — |
| 11 | qa | qa_checklist_skill.md |

## Salida

```
output/{slug}/
├── guion.json
├── shotlist.md      ← leer en el celular al grabar
├── qa_report.json
└── .checkpoint.json
```

Reintentar un agente: `--solo 02_hook` o `--desde 06_cta`.

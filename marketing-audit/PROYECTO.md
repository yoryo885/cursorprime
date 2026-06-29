# Marketing Audit

Pipeline cursorprime: **5 agentes en paralelo** → score 0-100 → `MARKETING-AUDIT.md` (+ PDF opcional).

Basado en [vendor/ai-marketing-claude](../vendor/ai-marketing-claude/) (Zubair Trabzada / AI Workshop).

## Comandos

```bash
cd ~/cursorprime/marketing-audit
pip install -r requirements.txt

# Demo (MOCK_FETCH=true por defecto)
python3 marketing_audit_main.py audit --url https://calendly.com --slug demo_audit

# Live fetch
MOCK_FETCH=false python3 marketing_audit_main.py audit --url https://ejemplo.com

# PDF + copia a cliente
python3 marketing_audit_main.py audit \
  --url https://ejemplo.com \
  --slug clinica-audit \
  --pdf \
  --cliente demo-kerkus \
  --proyecto black-friday

# Solo bridge
python3 marketing_audit_main.py bridge demo_audit --cliente demo-kerkus --proyecto black-friday

python3 marketing_audit_main.py listar
```

## Pipeline

```
Context → Discovery → ParallelAudit (5×) → Synthesis → QC → Packager → [PDF]
```

| Agente | Dimensión | Peso |
|--------|-----------|------|
| ContentAgent | Copy y mensaje | 25% |
| ConversionAgent | CRO | 20% |
| TechnicalAgent | SEO técnico | 20% |
| CompetitiveAgent | Competencia | 15% |
| StrategyAgent | Marca + growth | 10% + 10% |

Los 5 corren en **ThreadPoolExecutor** (paralelo real en Python).

## Salidas

```
data/{slug}/
├── inputs/brief.json
├── meta/
│   ├── discovery.json
│   ├── agents/{content,conversion,competitive,technical,strategy}.json
│   └── synthesis.json
└── output/
    ├── MARKETING-AUDIT.md
    ├── audit.json
    └── MARKETING-REPORT.pdf   # con --pdf
```

## Integración

| Proyecto | Rol |
|----------|-----|
| `clientes/` | Entregables vía `--cliente` / `--proyecto` |
| `vendor/ai-marketing-claude` | analyze_page + PDF script |
| Skill `market-audit` | Chat / router → este CLI |

## Env

Ver `.env.example` — `MOCK_FETCH=true` por defecto.

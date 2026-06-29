# Project Lens

Evaluador de ideas con **13 agentes**, scores con márgenes de error y confianza por métrica.

## Quick start

```bash
cd ~/cursorprime/project_lens
pip install -r requirements.txt
cp .env.example .env

# MVP (8 agentes, mock web)
python3 project_lens_main.py --slug demo-idea --modo mvp

# Full (13 agentes)
python3 project_lens_main.py --slug wasap-pymes --idea "../ideas de proyectos/ideas/wasap-pymes.json"

# V1 web real (trend pytrends + competition Playwright)
bash scripts/setup_web.sh
MOCK_WEB=false python3 project_lens_main.py --slug demo-idea --modo full --no-mock-web

### Competition — URLs y filtros

En `idea.json`:

```json
{
  "urls_referencia": ["https://wati.io/pricing/", "..."],
  "competencia": [
    {"url": "https://competidor.com/pricing", "notas": "opcional"}
  ],
  "competencia_filtros": {
    "precio_clp_min": 10000,
    "precio_clp_max": 350000,
    "max_urls": 10
  }
}
```

- Hasta **10 URLs** (`urls_referencia` + `competencia[]`)
- Filtra precios fuera de rango SaaS mensual CLP
- Quita outliers (IQR) y normaliza USD → CLP
- Reporta crudos vs usados vs descartados + mediana

**Market:** pendiente V1.5 (sigue heurístico).

# V2 compare
python3 project_lens_main.py --compare wasap-pymes demo-idea

# V2 mejoras
python3 project_lens_main.py --slug wasap-pymes --mejorar --aplicar-mejoras
```

## Modos

| Modo | Agentes | Web |
|------|---------|-----|
| **MVP** `--modo mvp` | context, financial, cost_mvp, synthesis, planner, qc, report, improvement | mock |
| **Full** `--modo full` | los 13 | mock por defecto |
| **V1** | trend (pytrends), competition (Playwright + filtros precio, hasta 10 URLs) | `--no-mock-web` + `bash scripts/setup_web.sh` |
| **V1.5** | market | **pendiente** — heurístico |
| **V2** | compare, canvas, `--aplicar-mejoras` | — |

## Estructura

```
project_lens/
├── project_lens_main.py
├── meta/constitution.json, weights.json, plan.json
├── data/{slug}/inputs/idea.json
├── data/{slug}/meta/*.json
├── data/{slug}/output/resumen.md, plan.md, dashboard.canvas.tsx
└── src/agents/   # 13 agentes
```

## Relación con `ideas de proyectos/`

- Input compartido: `../ideas de proyectos/ideas/{slug}.json`
- El evaluador simple (`evaluar.py`) es ligero; Project Lens es el análisis profundo con agentes.

## Skill Cursor

`~/.cursor/skills/project-lens/SKILL.md` — invocar con «usa project-lens».

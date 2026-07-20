# landing_pipeline

Pipeline de agentes (01–12) + skills `.md` por sección → `copy.json` + `landing.html` + `qa_report.json`.

## Uso

```bash
cd landing_pipeline
python3 landing_main.py run --demo
# o
python3 landing_main.py run --input meta/ejemplo-negocio.json --slug mi-marca
```

Reintento de un agente fallido:

```bash
python3 landing_main.py run --slug vertice-pro --retry-from 07_pricing
```

Solo un agente (usa checkpoint previo):

```bash
python3 landing_main.py run --slug vertice-pro --solo 11_design
```

## LLM

- Con `ANTHROPIC_API_KEY` en `.env` → Claude.
- Sin clave / `LANDING_MOCK=1` → copy determinista según skills (demo).

## Estructura

Ver prompt original. Skills en `src/skills/`. Outputs en `output/{slug}/`.

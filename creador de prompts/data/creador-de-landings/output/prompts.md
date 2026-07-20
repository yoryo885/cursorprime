# Prompt — Pipeline de agentes para landings

```
Usa landing-pipeline (landing_pipeline/).

Flujo obligatorio:
1. 01_brief → brief.json
2. 02_hero … 10_footer → cada uno LEE su skill .md y aporta a copy.json
3. 11_design → landing.html (un archivo, mobile-first)
4. 12_qa → qa_report.json (score + regenerar[])

Reglas:
- Cada agente: def run(input: dict) -> dict
- NO improvisar estilo: inyectar skill en system prompt
- Testimonios: no inventar
- Reintento: --retry-from {agente} sin re-correr todo
- Mock sin API key; Claude con ANTHROPIC_API_KEY

CLI:
  python3 landing_main.py run --demo
  python3 landing_main.py run --input meta/ejemplo-negocio.json --slug {slug}
```

# Prompt — Pipeline landings v2 (bugs reales)

```
Usa landing-pipeline (landing_pipeline/).

v2 — prevenir por diseño:
1. sanitize_prepend: nunca "desde desde"
2. secciones flujo normal: sin absolute/fixed de contenido
3. un solo --accent en todos los .btn
4. solo nombre_producto / propuesta_valor en copy público
5. testimonios: omitida:true + omisiones en qa_report (no silenciar)

Agentes 01–13 (13 = visual_qa Playwright + screenshots).
QA reporta bugs_v2 explícitamente.

CLI:
  python3 landing_main.py run --demo
```

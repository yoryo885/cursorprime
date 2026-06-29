# Estado — Análisis de proyectos

Actualizado: 2026-06-29

## Hecho

- [x] Pipeline 5 agentes (context → fetch → synthesis → QC → packager)
- [x] CLI: `analizar`, `radar`, `radar-auto`, `fetch-test`, `exportar`, `listar`
- [x] **Fetch live** — DuckDuckGo (`ddgs`), `.env` `MOCK_FETCH=false`, flag `--live`
- [x] **Radar automático** — `radar-auto` (1×/semana, salta si ya corrió, exporta idea)
- [x] Radar live probado: `data/radar-2026w27/` — 14 fuentes reales
- [x] Script cron: `scripts/radar-semanal.sh`
- [x] Plantilla launchd: `scripts/com.cursorprime.radar-kdp.plist`
- [x] Launchd instalado en Mac (`~/Library/LaunchAgents/com.cursorprime.radar-kdp.plist`)
- [x] Export → evaluar probado (radar-2026w27 → VIABLE 85/100)
- [x] Visible en centro de control (panel + pestaña Investigaciones)

- [x] Encadenar auto: analizar → lluvia → evaluar (`encadenar`, `--encadenar`, `auto_encadenar` en radar)

## Pendiente (no bloquea uso)

- [ ] Síntesis con LLM (hoy heurística por keywords)
- [ ] Informe HTML vendible (solo markdown)

## Comandos clave

```bash
cd ~/cursorprime/analisis-de-proyectos
pip install -r requirements.txt

python3 analisis_main.py fetch-test --texto "tu nicho"
python3 analisis_main.py analizar --texto "..." --live --exportar
python3 analisis_main.py radar-auto --exportar
python3 analisis_main.py radar-auto --exportar --encadenar
python3 analisis_main.py encadenar radar-2026w27
python3 analisis_main.py analizar --texto "..." --live --exportar --encadenar
```

## Automatizar radar (lunes 8:00)

```bash
cp scripts/com.cursorprime.radar-kdp.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cursorprime.radar-kdp.plist
```

Log: `logs/radar_cron.log`

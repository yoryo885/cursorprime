#!/bin/bash
# Radar KDP semanal — usar con cron o launchd
# Ejemplo cron (lunes 8:00): 0 8 * * 1 /Users/yoryo/cursorprime/analisis-de-proyectos/scripts/radar-semanal.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export MOCK_FETCH=false
exec python3 analisis_main.py radar-auto --exportar --encadenar >> logs/radar_cron.log 2>&1

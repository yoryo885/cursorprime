#!/usr/bin/env bash
# Abre el centro de control en el navegador (Mac / Linux)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "→ Regenerando panel…"
python3 panel_main.py refresh
PORT="${PORT:-8770}"
if curl -sf "http://127.0.0.1:${PORT}/panel.html" >/dev/null 2>&1; then
  echo "→ Servidor ya activo en puerto ${PORT}"
else
  echo "→ Levantando servidor en http://localhost:${PORT}/panel.html"
  python3 -m http.server "$PORT" --directory output >/dev/null 2>&1 &
  sleep 0.5
fi
URL="http://localhost:${PORT}/panel.html?v=$(date +%s)"
echo "→ Abrir: ${URL}"
if command -v open >/dev/null; then
  open "$URL"
elif command -v xdg-open >/dev/null; then
  xdg-open "$URL"
else
  echo "   Abre esa URL en el navegador manualmente."
fi

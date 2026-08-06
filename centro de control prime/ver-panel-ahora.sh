#!/usr/bin/env bash
# Fuerza panel nuevo — mata servidor viejo, regenera, abre navegador
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PORT="${PORT:-8770}"

echo "1/4 Matando servidores viejos en puerto ${PORT}…"
if command -v lsof >/dev/null; then
  lsof -ti:"${PORT}" | xargs kill -9 2>/dev/null || true
elif command -v fuser >/dev/null; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi
sleep 0.3

echo "2/4 git pull (trae UI español de main)…"
git -C "$(dirname "$ROOT")" pull origin main --ff-only 2>/dev/null || echo "   (sin git pull — sigue con carpeta local)"

echo "3/4 Regenerando panel…"
python3 panel_main.py refresh

echo "4/4 Servidor + navegador…"
python3 -m http.server "$PORT" --directory output >/tmp/centro-panel-server.log 2>&1 &
sleep 0.6
URL="http://127.0.0.1:${PORT}/panel.html?build=$(date +%s)"
echo ""
echo "════════════════════════════════════════════"
echo "  ABRE ESTA URL (debe tener BARRA VERDE arriba):"
echo "  ${URL}"
echo "════════════════════════════════════════════"
echo ""
if curl -sf "$URL" | grep -q "Versión nueva"; then
  echo "✓ Servidor OK — HTML nuevo confirmado"
else
  echo "✗ ADVERTENCIA: no se detectó barra verde en el HTML servido"
fi
if command -v open >/dev/null; then open "$URL"
elif command -v xdg-open >/dev/null; then xdg-open "$URL"
fi

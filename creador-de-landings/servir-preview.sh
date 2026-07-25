#!/usr/bin/env bash
# Sirve data/ en :8777 para ver demo-cliente y demo-simple
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT=8777

if curl -sf -o /dev/null --connect-timeout 1 "http://127.0.0.1:${PORT}/demo-cliente/output/preview.html"; then
  echo "OK ya sirve → http://127.0.0.1:${PORT}/demo-cliente/output/preview.html"
  echo "             → http://127.0.0.1:${PORT}/demo-simple/output/preview.html"
  exit 0
fi

cd "$ROOT/data"
echo "Iniciando http.server en ${PORT} (bind 127.0.0.1)…"
exec python3 -m http.server "$PORT" --bind 127.0.0.1

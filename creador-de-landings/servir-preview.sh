#!/usr/bin/env bash
# Arranca (o reutiliza) el preview en :8777
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/data/demo-cliente/output"
PORT=8777

if curl -sf -o /dev/null --connect-timeout 1 "http://127.0.0.1:${PORT}/preview.html"; then
  echo "OK ya sirve → http://localhost:${PORT}/preview.html"
  exit 0
fi

cd "$OUT"
echo "Iniciando http.server en ${PORT}…"
exec python3 -m http.server "$PORT" --bind 0.0.0.0

#!/usr/bin/env bash
# Sirve el panel con acceso a clientes/, data/, centro de control prime/
cd "$(dirname "$0")/.." || exit 1
echo "Panel → http://127.0.0.1:8766/PANEL-CONTROL.html"
python3 -m http.server 8766 --bind 127.0.0.1

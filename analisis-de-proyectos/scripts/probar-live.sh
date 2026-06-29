#!/bin/bash
# Instala dependencias y prueba fetch live + radar automático
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m pip install -r requirements.txt -q
echo "→ fetch-test"
python3 analisis_main.py fetch-test --texto "kdp resumenes libros youtube"
echo ""
echo "→ radar-auto (live, export)"
python3 analisis_main.py radar-auto --exportar --force --reset-checkpoint

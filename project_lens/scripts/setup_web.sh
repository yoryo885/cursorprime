#!/usr/bin/env bash
# Setup web real — Project Lens V1
set -euo pipefail
cd "$(dirname "$0")/.."

echo "→ Instalando dependencias Python..."
pip install -r requirements.txt

echo "→ Instalando Chromium para Playwright..."
python3 -m playwright install chromium

echo ""
echo "✅ Listo. Prueba:"
echo "   MOCK_WEB=false python3 project_lens_main.py --slug demo-idea --modo full --no-mock-web"

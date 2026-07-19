#!/usr/bin/env bash
# Regenera sitio-pdf y copia todo a esta carpeta landing.
set -euo pipefail
LANDING="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$(cd "$LANDING/../../../.." && pwd)"
SITIO="$WORKSPACE/sitio-pdf"
OUT="$SITIO/data/vertice-pro/output"

cd "$SITIO"
python3 sitio_pdf_main.py generar --slug vertice-pro --producto pareto --mock --reset-checkpoint

cp "$OUT/preview.html" "$LANDING/preview/index.html"
cp -r "$OUT/assets/"* "$LANDING/preview/assets/"
cp "$OUT/vertice-pro-theme.zip" "$LANDING/shopify/"

echo "✅ Landing actualizada: $LANDING"

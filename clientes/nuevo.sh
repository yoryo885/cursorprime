#!/usr/bin/env bash
# Uso: ./nuevo.sh slug-cliente [slug-proyecto]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SLUG_CLIENTE="${1:?Falta slug-cliente: ./nuevo.sh mi-cliente mi-campana}"
SLUG_PROYECTO="${2:-campana-inicial}"

DEST="$ROOT/$SLUG_CLIENTE"
if [[ -e "$DEST" ]]; then
  echo "Error: ya existe $DEST"
  exit 1
fi

TEMPLATE_PROY="$ROOT/_plantilla/proyectos/_ejemplo"
PIPELINE_SLUG="${SLUG_CLIENTE}-${SLUG_PROYECTO}"

cp -r "$ROOT/_plantilla" "$DEST"
rm -rf "$DEST/proyectos/_ejemplo"

PROY="$DEST/proyectos/$SLUG_PROYECTO"
mkdir -p "$PROY/.cursor/rules"
mkdir -p "$PROY/entregables"/{estrategia,copy,visual}
cp "$TEMPLATE_PROY/brief.json" "$PROY/"
cp "$TEMPLATE_PROY/CONTEXTO.md" "$PROY/"
cp "$TEMPLATE_PROY/.cursor/rules/proyecto.mdc" "$PROY/.cursor/rules/"

replace() {
  if sed --version >/dev/null 2>&1; then
    sed -i "$@"
  else
    sed -i '' "$@"
  fi
}

# Cliente
replace "s/slug-cliente/$SLUG_CLIENTE/g" \
  "$DEST/CLIENTE.md" \
  "$DEST/perfil.json" \
  "$DEST/.cursor/rules/cliente.mdc" \
  "$DEST/.cursor/rules/enrutamiento-equipo.mdc"

replace "s/\"slug\": \"slug-cliente\"/\"slug\": \"$SLUG_CLIENTE\"/g" "$DEST/perfil.json"

# Proyecto
replace "s/cliente-slug-ejemplo/$PIPELINE_SLUG/g" \
  "$PROY/brief.json" \
  "$PROY/CONTEXTO.md" \
  "$PROY/.cursor/rules/proyecto.mdc"

replace "s/\"slug\": \"ejemplo\"/\"slug\": \"$SLUG_PROYECTO\"/g" "$PROY/brief.json"
replace "s/\"cliente_slug\": \"slug-cliente\"/\"cliente_slug\": \"$SLUG_CLIENTE\"/g" "$PROY/brief.json"
replace "s/slug-cliente/$SLUG_CLIENTE/g" "$PROY/.cursor/rules/proyecto.mdc"
replace "s/proyectos\\/ejemplo/proyectos\\/$SLUG_PROYECTO/g" "$PROY/.cursor/rules/proyecto.mdc"

echo "Cliente:  $DEST"
echo "Proyecto: $PROY"
echo "Pipeline slug: $PIPELINE_SLUG"
echo ""
echo "Siguiente:"
echo "  1. Edita CLIENTE.md y perfil.json"
echo "  2. Edita brief.json y CONTEXTO.md"
echo "  3. Chat: @clientes/$SLUG_CLIENTE/proyectos/$SLUG_PROYECTO/"

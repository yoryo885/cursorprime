#!/usr/bin/env bash
# Abre el centro de control en el navegador (Mac / Linux)
# Si ves la versión vieja → usa ver-panel-ahora.sh (mata cache y servidor)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/ver-panel-ahora.sh"

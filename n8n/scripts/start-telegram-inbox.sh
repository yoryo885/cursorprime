#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/runner"
set -a
# shellcheck disable=SC1091
source "$ROOT/.env"
set +a
exec python3 telegram_inbox.py

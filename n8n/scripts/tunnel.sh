#!/usr/bin/env bash
# Tunnel Cloudflare → n8n local (URL para celular)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${N8N_PORT:-5678}"
OUT="$ROOT/URL-PUBLICA.txt"

if ! curl -sf -o /dev/null --connect-timeout 2 "http://127.0.0.1:${PORT}/"; then
  echo "n8n no responde en :${PORT}. Arrancá primero: npm start"
  exit 1
fi

if [[ ! -x /tmp/cloudflared ]]; then
  curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    -o /tmp/cloudflared
  chmod +x /tmp/cloudflared
fi

echo "Creando tunnel… (dejá este proceso abierto)"
# Imprime URL y la guarda
/tmp/cloudflared tunnel --url "http://127.0.0.1:${PORT}" --no-autoupdate 2>&1 | tee /tmp/n8n-tunnel.log | while IFS= read -r line; do
  echo "$line"
  if [[ "$line" =~ https://[a-zA-Z0-9.-]+\.trycloudflare\.com ]]; then
    url=$(echo "$line" | grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' | head -1)
    echo "$url" > "$OUT"
    echo ""
    echo "✅ Abrí en el celular: $url"
    echo "   (usuario/clave de .env)"
  fi
done

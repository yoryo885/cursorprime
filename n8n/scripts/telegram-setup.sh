#!/usr/bin/env bash
# Resuelve TELEGRAM_CHAT_ID mirando getUpdates (después de /start al bot).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
set -a
# shellcheck disable=SC1091
source "$ROOT/.env"
set +a

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "Falta TELEGRAM_BOT_TOKEN en n8n/.env"
  echo "1) Abrí Telegram → @BotFather → /newbot"
  echo "2) Pegá el token en .env"
  echo "3) Abrí tu bot y mandá /start"
  echo "4) Volvé a correr: bash scripts/telegram-setup.sh"
  exit 1
fi

export TELEGRAM_USERNAME="${TELEGRAM_USERNAME:-yoryo321}"
echo "Buscando chat de @${TELEGRAM_USERNAME} en getUpdates…"
raw=$(curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates")
echo "$raw" | TELEGRAM_USERNAME="$TELEGRAM_USERNAME" ROOT="$ROOT" python3 -c '
import json, os, sys
data = json.load(sys.stdin)
want = (os.environ.get("TELEGRAM_USERNAME") or "yoryo321").lstrip("@").lower()
root = os.environ["ROOT"]
found = None
matched_user = False
for u in data.get("result") or []:
    msg = u.get("message") or u.get("edited_message") or {}
    chat = msg.get("chat") or {}
    user = msg.get("from") or {}
    uname = (user.get("username") or chat.get("username") or "").lower()
    if uname == want:
        found = chat.get("id")
        matched_user = True
        break
    if found is None and chat.get("type") == "private":
        found = chat.get("id")
if not found:
    print("No encontré mensajes. Abrí el bot en Telegram y mandá /start, después reintentá.")
    sys.exit(2)
print(f"CHAT_ID={found}" + (" (match @" + want + ")" if matched_user else " (último chat privado)"))
env_path = os.path.join(root, ".env")
text = open(env_path, encoding="utf-8").read()
lines = []
done = False
for line in text.splitlines():
    if line.startswith("TELEGRAM_CHAT_ID="):
        lines.append(f"TELEGRAM_CHAT_ID={found}")
        done = True
    else:
        lines.append(line)
if not done:
    lines.append(f"TELEGRAM_CHAT_ID={found}")
open(env_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
cfg_path = os.path.join(root, "runner", "config.json")
cfg = json.load(open(cfg_path, encoding="utf-8"))
cfg.setdefault("telegram", {})["chat_id"] = found
json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Guardado en .env y runner/config.json")
print("Reiniciá el runner y probá telegram.notify")
'

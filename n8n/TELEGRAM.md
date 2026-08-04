# Telegram — entrega a @yoryo321

Destino guardado: **@yoryo321**

## Activar (2 minutos)

1. En Telegram abrí **@BotFather** → `/newbot` → elegí nombre.
2. Copiá el **token**.
3. Pegalo en `n8n/.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   ```
4. Abrí **tu bot** (el que creaste) y mandá `/start`.
5. Corré:
   ```bash
   cd n8n && bash scripts/telegram-setup.sh
   ```
6. Reiniciá el runner. Probá un lead o:
   ```bash
   curl -X POST http://127.0.0.1:8780/job \
     -H 'Content-Type: application/json' \
     -d '{"action":"telegram.notify","payload":{"text":"Hola"}}'
   ```

Leads y briefs TikTok ya intentan avisar a Telegram automáticamente.

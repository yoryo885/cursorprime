# n8n — cursorprime

Automatización con n8n, pensada para usarse **desde el celular** (URL pública).

## Arranque rápido (en este entorno / VPS)

```bash
cd n8n
npm install
cp .env.example .env   # editar usuario/clave
npm start              # UI en http://127.0.0.1:5678
bash scripts/tunnel.sh # URL https://….trycloudflare.com
```

Abrí la URL del tunnel en el **celular**. Login con `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`.

## Qué guarda GitHub

| En repo | Fuera de repo (local) |
|---------|------------------------|
| `workflows/*.json` (exports) | `data/`, `.n8n/`, `node_modules/` |
| scripts de start/tunnel | `.env` (secretos) |

## Celular / iPad

1. `npm start` + tunnel
2. Abrís la URL HTTPS en Safari/Chrome del teléfono
3. Creás un workflow con nodo **Webhook** → Activate
4. Pegás esa webhook URL al agente Cursor para disparar flujos

## Importante

El tunnel de este Cloud Agent **expira** cuando se apaga el pod.  
Para uso diario permanente: [n8n.cloud](https://n8n.cloud) o un VPS; los JSON de `workflows/` se importan igual.

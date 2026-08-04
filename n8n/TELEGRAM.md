# Telegram — @yoryo321

Bot: **@mi_asistente_yoryo_bot**

## Qué llega

- Avisos de leads
- **Videos MP4** del Creador de Contenido (Cursor) como archivo en el chat
- Briefs / audits en texto

## Comandos

| Escribís | Qué hace |
|----------|----------|
| `ayuda` | Lista |
| `video TEMA` | Genera video (slideshow) y te lo manda |
| `correr` | Lead + audit + **video a Telegram** |
| `audit …` / `tiktok …` / `leads` / `status` | Como antes |

## Arrancar

```bash
cd n8n
bash scripts/start-runner.sh
bash scripts/start-telegram-inbox.sh
```

n8n webhook (opcional): `POST /webhook/contenido/video-telegram`  
body: `{"tema":"3 errores en Google"}`

# Telegram — @yoryo321

Bot: **@mi_asistente_yoryo_bot**

## Qué llega

- Avisos de leads
- **Videos MP4 CON personaje** (modo animado del Creador de Contenido) como archivo en el chat
- Briefs / audits en texto

## Default del sistema

`video` y `correr` generan **animado + personaje** (emprendedor + guía).  
No usan slideshow de cards salvo que se pida `modo: slideshow` a propósito en el runner.

## Comandos

| Escribís | Qué hace |
|----------|----------|
| `ayuda` | Lista |
| `video TEMA` | Genera video **con personaje** y te lo manda |
| `correr` | Lead + audit + **video con personaje** |
| `audit …` / `tiktok …` / `leads` / `status` | Como tienen documentado |

## Arrancar

```bash
cd n8n
bash scripts/start-runner.sh
bash scripts/start-telegram-inbox.sh
```

n8n webhook (opcional): `POST /webhook/contenido/video-telegram`  
body: `{"tema":"emprendedor ordena WhatsApp","modo":"animado"}`

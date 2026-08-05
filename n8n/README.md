# n8n — cursorprime

## Modo actual: solo sistemas (sin login)

No estamos usando la UI de n8n ahora.  
Los flujos viven en GitHub y se **importan después** (n8n.cloud o VPS).

→ Catálogo: **[SISTEMAS.md](./SISTEMAS.md)**  
→ Archivos: `sistemas/{id}/workflow.json`

## Cuando quieras encenderlo

```bash
cd n8n
npm install
cp .env.example .env
npm start
bash scripts/tunnel.sh   # URL para celular
```

Luego: Import from File → cada `workflow.json` → Activate.

## Qué va a git

| Sí | No |
|----|----|
| `sistemas/**` | `data/`, `node_modules/`, `.env` |
| scripts + README | `URL-PUBLICA.txt` |

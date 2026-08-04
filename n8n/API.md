# n8n API habilitada

## UI
`https://abroad-differential-rolled-counters.trycloudflare.com`

## API
- Base: `{URL}/api/v1`
- Swagger: `{URL}/api/v1/docs`
- Header: `X-N8N-API-KEY`

Credenciales y key: `.credentials-local.md` + `.api-key` (gitignored).

```bash
export N8N_URL=$(cat URL-PUBLICA.txt)
export N8N_API_KEY=$(cat .api-key)
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/api/v1/workflows"
```

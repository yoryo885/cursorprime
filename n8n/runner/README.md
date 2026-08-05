# Runner cursorprime

Puente **n8n → disco / jobs** para que el embudo y los sistemas empiecen a funcionar sin nodos grises a `:9999`.

## Arrancar

```bash
cd n8n
bash scripts/start-runner.sh
# o: python3 runner/runner_main.py
```

Escucha: `http://127.0.0.1:8780`

## Endpoints

| Método | Path | Qué hace |
|--------|------|----------|
| GET | `/health` | Estado + conteo leads/jobs |
| GET | `/leads` | Últimos leads |
| POST | `/job` | Ejecuta una `action` |

### Actions

- `ping`
- `lead.append` — guarda lead + job seguimiento
- `job.enqueue`
- `pipeline.tiktok_brief` — escribe brief en `creador de contenido/data/{slug}/inputs/`
- `pipeline.audit_demo` — brief + job audit en cola

## Datos

- Leads: `runner/data/leads.jsonl` (gitignored)
- Jobs: `runner/jobs/*.json` (gitignored)

## Ciclo de revisión

Todo lo que genera el runner es **borrador**. Si no te gusta PDF/video/copy: pedile a Cursor el cambio — no lo editás a mano.

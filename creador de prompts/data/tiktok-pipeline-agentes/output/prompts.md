# Prompts — TikTok pipeline (aparte del PDF)

- **Slug:** tiktok-pipeline-agentes
- **Proyecto:** tiktok-pipeline

## Regla de frontera (obligatoria)

1. **No modificar** `libros a entender` ni el PDF/markdown generado.
2. Este pipeline es **aparte**.
3. **Sí puede leer** la salida (`resumenes/{slug}/*.md` o `.pdf`) en solo lectura.
4. **Pesca ideas centrales** → las transforma en hook, guion, shotlist y caption de video.
5. Todo el contenido nuevo vive en `tiktok_pipeline/output/{slug}/`.

## Prompt operativo

```
Usa tiktok_pipeline (no toques libros a entender).

Pesca ideas del resumen/PDF con --fuente (solo lectura) y genera shotlist:

cd tiktok_pipeline
MOCK_LLM=true python3 tiktok_main.py \
  --fuente "../libros a entender/resumenes/{slug}/{Libro}.md" \
  --nicho "{audiencia}" \
  --slug video_{slug} \
  --reset-checkpoint

Entrega: output/video_{slug}/shotlist.md + ideas_centrales en guion.json.
```

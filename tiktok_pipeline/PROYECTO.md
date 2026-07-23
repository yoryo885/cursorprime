# TikTok Pipeline

Pipeline **aparte** de `libros a entender`. No modifica PDFs ni el sistema de libros.

Lee (solo lectura) un resumen/PDF ya generado → pesca ideas centrales → arma guion TikTok (hook, script, shotlist, etc.).

## Comando

```bash
cd tiktok_pipeline
pip install -r requirements.txt

# Desde un resumen de libros a entender (NO lo modifica)
MOCK_LLM=true python3 tiktok_main.py \
  --fuente "../libros a entender/resumenes/pareto/El principio de Pareto - Antoine Delers.md" \
  --nicho "psicopedagogia" \
  --slug demo_desde_fuente \
  --reset-checkpoint

# Solo con tema (sin fuente)
MOCK_LLM=true python3 tiktok_main.py --tema "Principio de Pareto" --nicho "productividad"
```

## Flujo

```
fuente .md/.pdf (solo lectura)
        ↓
00_extract_fuente  → ideas_centrales
        ↓
01…11  → hook, script, cortes, CTA, shotlist, QA
        ↓
output/{slug}/shotlist.md   (nuevo contenido de video)
```

## Regla de frontera

| Proyecto | Rol |
|----------|-----|
| `libros a entender` | Genera PDF/resumen — **no se toca** |
| `tiktok_pipeline` | Pesca ideas y crea guion de video — **aparte** |

## Agentes

| # | Agente | Skill |
|---|--------|-------|
| 00 | extract_fuente | extract_fuente_skill.md |
| 01 | trend_research | — |
| 02 | hook | hook_skill.md |
| 03 | script | script_skill.md |
| 04–09 | interrupts → captions | skills correspondientes |
| 10 | shotlist | — |
| 11 | qa | qa_checklist_skill.md |

## Salida

```
output/{slug}/
├── guion.json       ← incluye ideas_centrales + fuente_extract
├── shotlist.md
├── qa_report.json
└── .checkpoint.json
```

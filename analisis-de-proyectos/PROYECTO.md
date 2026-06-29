# Análisis de proyectos

**Sistema de análisis para crear proyectos.** Investiga qué funciona hoy (YouTube, web) y produce un informe listo para convertirse en pipeline.

## Flujo

```
YouTube + sitios  →  analizar  →  analisis.json/md  →  exportar  →  ideas de proyectos
                                                              ↓
                                                    lluvia-de-ideas (propuestas + tu OK)
```

## Comandos

```bash
cd "/Users/yoryo/cursorprime/analisis-de-proyectos"
pip install -r requirements.txt

# Analizar un nicho
python3 analisis_main.py analizar --texto "resumenes libros kdp youtube"

# Analizar + exportar borrador de proyecto
python3 analisis_main.py analizar --texto "packs visuales amazon" --exportar

# Radar KDP semanal (fetch live)
python3 analisis_main.py radar --live

# Radar automático — 1 vez/semana, exporta idea si no corrió
python3 analisis_main.py radar-auto --exportar

# Probar solo fetch sin pipeline
python3 analisis_main.py fetch-test --texto "kdp resumenes libros"

# Analizar con fetch real
python3 analisis_main.py analizar --texto "packs visuales amazon" --live --exportar

# Exportar análisis existente
python3 analisis_main.py exportar demo_investigacion

# Ver análisis guardados
python3 analisis_main.py listar
```

## Salidas

```
data/{slug}/
├── inputs/brief.json
├── meta/analisis.json
└── output/analisis.md
```

Exportación:

```
ideas de proyectos/ideas/from-analisis/{slug}.json
```

## Relación con otros proyectos

| Proyecto | Rol |
|----------|-----|
| **analisis-de-proyectos** | Investigar + analizar (esta carpeta) |
| **lluvia-de-ideas** | Propone mejoras; tú apruebas |
| **ideas de proyectos** | Evalúa y diseña el pipeline |
| **creador de contenido** | Pack visual post-análisis |

## MOCK vs live

| Modo | Config | Comando |
|------|--------|---------|
| Demo | `MOCK_FETCH=true` | `python3 analisis_main.py analizar --texto "..."` |
| **Live** | `MOCK_FETCH=false` en `.env` | `python3 analisis_main.py analizar --texto "..." --live` |

Probar solo fetch: `python3 analisis_main.py fetch-test --texto "tu nicho"`

## Radar semanal automático

```bash
# Una vez por semana (salta si ya corrió)
python3 analisis_main.py radar-auto --exportar

# Forzar repetir
python3 analisis_main.py radar-auto --force --exportar

# Script cron (lunes 8:00)
./scripts/radar-semanal.sh
```

**macOS launchd** (opcional):

```bash
cp scripts/com.cursorprime.radar-kdp.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cursorprime.radar-kdp.plist
```

Log: `logs/radar_cron.log`

# PDF Resumidor — Especificación

Documento maestro para construir e invocar el agente resumidor de PDF.
Cuando esté listo para código, di: **`construye pdf-resumidor`**

---

## Qué hace

Recibe uno o más PDFs y genera un **resumen estructurado en JSON + markdown**, listo para alimentar Project Lens u otros pipelines.

No inventa datos: extrae, condensa y cita página/sección de origen.

---

## Invocación (nombre oficial)

```
usa pdf-resumidor
```

Variantes:
- `usa pdf-resumidor` + ruta al PDF
- `usa pdf-resumidor` + carpeta con PDFs
- `construye pdf-resumidor` → genera el código del pipeline

---

## Entrada

| Tipo | Ejemplo |
|------|---------|
| PDF suelto | `inputs/informe-mercado.pdf` |
| Carpeta | `inputs/pdfs/` |
| Opciones | `--tipo informe|plan|legal|tecnico` |

---

## Salida

```
data/{slug}/
├── meta/
│   ├── extraccion.json      # texto por página
│   ├── resumen.json         # resumen estructurado
│   └── qc_result.json       # validación
└── output/
    ├── resumen.md           # legible para humano
    └── resumen_corto.txt    # 5-10 líneas
```

### Schema resumen.json

```json
{
  "archivo": "informe-mercado.pdf",
  "paginas": 24,
  "confidence": 0.85,
  "tipo_detectado": "informe",
  "titulo": "...",
  "resumen_ejecutivo": "...",
  "puntos_clave": ["..."],
  "datos_numericos": [
    {"metrica": "TAM", "valor": "USD 2.1B", "pagina": 12, "confidence": 0.7}
  ],
  "entidades": {"empresas": [], "mercados": [], "fechas": []},
  "citas": [{"pagina": 5, "extracto": "..."}],
  "warnings": ["PDF escaneado — OCR con menor confidence"]
}
```

---

## Pipeline (6 pasos)

| id | slug | agente | qué hace |
|----|------|--------|----------|
| 1 | loader | PdfLoaderAgent | Valida PDF, detecta tipo (texto vs escaneado) |
| 2 | extract | PdfExtractAgent | Extrae texto (pdfplumber; OCR si escaneado) |
| 3 | chunk | ChunkAgent | Divide en secciones manejables |
| 4 | summarize | SummarizeAgent | Resume por sección + ejecutivo (LLM opcional) |
| 5 | qc | PdfQcAgent | Detecta páginas vacías, datos sin cita, alucinaciones |
| 6 | packager | PdfPackagerAgent | Escribe JSON + markdown |

---

## Agentes — responsabilidad

| Agente | Función |
|--------|---------|
| **PdfLoaderAgent** | Abre PDF, cuenta páginas, detecta si necesita OCR |
| **PdfExtractAgent** | Texto crudo por página con número de página |
| **ChunkAgent** | Agrupa por capítulos o bloques de ~2000 tokens |
| **SummarizeAgent** | Resumen ejecutivo + puntos clave + datos numéricos citados |
| **PdfQcAgent** | Todo dato numérico debe tener `pagina`; confidence < 0.5 → warning |
| **PdfPackagerAgent** | Entrega final en `output/` |

---

## Conexión con Project Lens

Si el PDF es un plan de negocio o informe de mercado:

```bash
# 1. Resumir PDF
python pdf_resumidor_main.py --pdf inputs/plan.pdf --slug mi-idea

# 2. El resumen alimenta la idea
# output/resumen.json → se copia/mapa a ideas/mi-idea.json
# 3. Analizar idea
usa project-lens --slug mi-idea
```

---

## Stack

- Python 3.9+
- `pdfplumber` — PDF con texto
- `pytesseract` + `pdf2image` — PDF escaneado (V1)
- `anthropic` — SummarizeAgent (opcional MVP: extractivo sin LLM)
- JSON en disco, CLI argparse

---

## MVP vs V1

**MVP:** loader + extract + summarize extractivo (sin LLM) + qc + packager

**V1:** OCR, LLM para resumen semántico, batch carpeta, link auto a project-lens

---

## Definition of Done

- [ ] `python pdf_resumidor_main.py --help` funciona
- [ ] PDF de prueba genera `resumen.json` + `resumen.md`
- [ ] QC detecta dato sin página de origen
- [ ] `--slug` compatible con estructura Project Lens

---

## Comandos previstos

```bash
python pdf_resumidor_main.py --pdf ruta/al/archivo.pdf
python pdf_resumidor_main.py --carpeta inputs/pdfs/ --batch
python pdf_resumidor_main.py --slug mi-idea --desde-paso 3
python pdf_resumidor_main.py --sin-qc
```

---

*Generado como spec maestro. Código pendiente hasta: `construye pdf-resumidor`*

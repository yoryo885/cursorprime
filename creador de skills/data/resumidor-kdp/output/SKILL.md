---
name: resumidor-kdp
description: >-
  Flujo completo PDF → resumen editorial → listing Amazon KDP en libros a
  entender. Producción con main.py; marketing con kdp_main.py (solo lee el PDF).
  Proyecto: Libros a entender. Usar cuando el usuario pide resumidor kdp, pdf
  resumen amazon, marketing kdp, listing amazon, usa resumidor-kdp, o publicar
  un resumen en KDP.
---

# Resumidor KDP

Skill de **workflow** para Libros a entender.

## Cuándo usar

Activar cuando el usuario diga: resumidor kdp, pdf resumen amazon, marketing kdp, usa resumidor-kdp, listing amazon.

**No confundir con `pdf-resumidor`:** ese skill es para extraer datos de PDFs genéricos (Project Lens). Este flujo genera **resúmenes editoriales Yordy** y **copy para Amazon KDP**.

## Proceso

PDF fuente → resumen editorial (`main.py`) → aprobación usuario → listing KDP (`kdp_main.py`). Marketing **solo lee** el PDF; nunca lo regenera ni modifica.

## Pasos

1. **Preparar entrada**: PDF en `libros/{Libro}.pdf`. Confirmar `slug` y lista de temas con el usuario.
2. **Producción (contenido + PDF)**:
   ```bash
   cd ~/cursorprime/libros\ a\ entender
   python3 main.py --slug {slug} --sin-confirmacion "{Libro}" "Tema 1" "Tema 2" ...
   ```
   Salida: `resumenes/{slug}/{Libro}.md`, `{Libro}.pdf`, `meta/`, `tablas/`, `mapa/`.
3. **Aprobación**: mostrar PDF al usuario. **No correr marketing** hasta aprobación explícita.
4. **Marketing KDP**:
   ```bash
   python3 kdp_main.py --slug {slug}
   # o: python3 kdp_main.py "resumenes/{slug}/{Libro}.pdf"
   ```
   Salida: `resumenes/{slug}/kdp/amazon_listing.json`, `amazon_listing.txt`.
5. **QC listing**: título, descripción, keywords, beneficios. Si el PDF tiene problemas → `logs/produccion_solicitudes.json` vía producción (`main.py`), **no** desde marketing.

## Reglas

- Aprobación usuario obligatoria en PDF final antes de `kdp_main.py`.
- Constitución marketing: `marketing-constitucion.mdc` — marketing **SOLO LEE** el PDF.
- Si `producto.json` tiene `portada_aprobada: true` → no solicitar cambios de portada.
- Iterar diseño sin re-resumir: `--solo-pdf`, `--solo-tablas`, `--solo-mapa`, `--solo-enriquecer`.
- Requiere `ANTHROPIC_API_KEY` en `.env` para producción y marketing con LLM.
- Ruta base: `~/cursorprime/libros a entender`

## Proyecto

Carpeta: `../libros a entender` · Contexto: `CONTEXTO_PROYECTO.md` · Ramas: `RAMAS.md`

## Iteración

Si el resultado no encaja, pedir feedback y actualizar esta skill (v2 en misma carpeta).

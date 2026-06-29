"""Genera PDF desde el .md existente + tablas PNG (sin imágenes Unsplash)."""
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from src.agents._paths import tema_slug
from src.config import VOZ_NOMBRE
from src.agents.pdf_design_agent import clean_intro_text
from src.output_paths import resolve_intro_path, resolve_mapa_png
from src.md_loader import find_summary_md, parse_enriched_markdown


def _p(text: str, style) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def build_pdf_from_markdown(
    output_dir: Path,
    *,
    libro_nombre: str = "",
    sin_imagenes_unsplash: bool = True,
) -> Path:
    output_dir = Path(output_dir)
    md_path = find_summary_md(output_dir)
    libro, resultados, tablas, fecha = parse_enriched_markdown(md_path)
    libro = libro_nombre or libro

    intro_file = resolve_intro_path(output_dir)
    intro = clean_intro_text(
        intro_file.read_text(encoding="utf-8").strip()
        if intro_file.exists()
        else (
            f"Recopilo aquí lo que aprendí al leer «{libro}», "
            f"con mis propias palabras y conexiones con la vida real."
        )
    )

    safe = "".join(c if c.isalnum() or c in " -_," else "_" for c in libro).strip()[:80]
    pdf_path = output_dir / f"{safe or 'resumen'}.pdf"

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        spaceAfter=14,
        alignment=TA_CENTER,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=18,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=10,
        textColor="#555555",
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    quote_style = ParagraphStyle(
        "Quote",
        parent=styles["Normal"],
        fontSize=10,
        leftIndent=18,
        textColor="#333333",
        spaceAfter=4,
    )

    tablas_map = {t.tema: t for t in tablas}
    page_w, page_h = A4
    margin = 2 * cm
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin

    story = []
    story.append(_p(libro, title_style))
    story.append(_p(f"Resumen personal de {VOZ_NOMBRE}", meta_style))
    story.append(
        _p((fecha or datetime.now()).strftime("%d/%m/%Y"), meta_style)
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(_p(intro, body_style))
    story.append(PageBreak())

    mapa = resolve_mapa_png(output_dir)
    if mapa:
        story.append(_p("Mapa conceptual", h2_style))
        story.append(_scaled_image(mapa, avail_w, avail_h * 0.85))
        story.append(PageBreak())

    for resultado in resultados:
        if resultado.fallo:
            continue

        story.append(_p(resultado.tema, h2_style))
        texto = resultado.resumen_voz or resultado.resumen
        if texto:
            for parrafo in texto.split("\n\n"):
                parrafo = parrafo.strip()
                if parrafo:
                    story.append(_p(parrafo, body_style))

        tabla = tablas_map.get(resultado.tema)
        img_path = None
        if tabla and tabla.image_path and Path(tabla.image_path).exists():
            img_path = Path(tabla.image_path)
        else:
            slug = tema_slug(resultado.tema)
            candidato = output_dir / "tablas" / f"{slug}.png"
            if candidato.exists() and candidato.stat().st_size > 5000:
                img_path = candidato

        if img_path:
            story.append(Spacer(1, 0.3 * cm))
            story.append(_p("Tabla", styles["Heading3"]))
            story.append(_scaled_image(img_path, avail_w, avail_h * 0.55))

        if resultado.fragmentos:
            story.append(Spacer(1, 0.2 * cm))
            story.append(_p("Ideas del PDF", styles["Heading3"]))
            for i, frag in enumerate(resultado.fragmentos, 1):
                story.append(_p(f"{i}. {frag}", quote_style))

        story.append(PageBreak())

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=libro,
    )
    doc.build(story)
    return pdf_path


def _scaled_image(path: Path, max_w: float, max_h: float) -> Image:
    from reportlab.lib.utils import ImageReader

    reader = ImageReader(str(path))
    iw, ih = reader.getSize()
    scale = min(max_w / iw, max_h / ih, 1.0)
    return Image(str(path), width=iw * scale, height=ih * scale)

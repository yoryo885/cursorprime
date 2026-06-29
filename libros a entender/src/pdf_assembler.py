from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, SimpleDocTemplate


def assemble_images_pdf(
    image_paths: list[Path],
    output_path: Path,
    title: str = "Resumen",
) -> Path:
    """Combina imágenes PNG en un PDF de una página por imagen."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_w, page_h = A4
    margin = 1.2 * cm
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin

    story = []
    valid_paths = [Path(p) for p in image_paths if Path(p).exists()]

    for i, path in enumerate(valid_paths):
        reader = ImageReader(str(path))
        iw, ih = reader.getSize()
        scale = min(avail_w / iw, avail_h / ih)
        img = Image(str(path), width=iw * scale, height=ih * scale)
        story.append(img)
        if i < len(valid_paths) - 1:
            story.append(PageBreak())

    if not story:
        raise ValueError("No hay imágenes válidas para armar el PDF")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=title,
    )
    doc.build(story)
    return output_path

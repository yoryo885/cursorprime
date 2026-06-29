import re
import unicodedata
from pathlib import Path

from src.config import RESUMENES_DIR


def slugify(text: str) -> str:
    """Convierte texto a slug seguro para nombres de carpeta."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "libro"


def get_book_slug(pdf_path: Path, custom_slug: str = "") -> str:
    """
    Deriva un slug único por libro para aislar su carpeta de salida.
    Ej: '... - Daniel Kahneman.pdf' → 'kahneman'
    """
    if custom_slug:
        return slugify(custom_slug)

    stem = pdf_path.stem
    if " - " in stem:
        author = stem.rsplit(" - ", 1)[-1].strip()
        parts = author.split()
        if parts:
            return slugify(parts[-1])

    return slugify(stem)


def get_book_output_dir(pdf_path: Path, custom_slug: str = "") -> Path:
    """Ruta aislada de salida: resumenes/{slug}/"""
    slug = get_book_slug(pdf_path, custom_slug)
    output_dir = RESUMENES_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

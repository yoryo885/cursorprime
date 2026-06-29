import hashlib
from pathlib import Path

from pypdf import PdfReader

from src.config import PDF_CACHE_DIR


def extract_text(pdf_path: Path, use_cache: bool = True) -> str:
    """Extrae texto del PDF, usando caché si el archivo no cambió."""
    pdf_path = Path(pdf_path)
    cache_path = _cache_path(pdf_path)

    if use_cache and cache_path.exists():
        print(f"   📦 Texto PDF desde caché ({cache_path.name})")
        return cache_path.read_text(encoding="utf-8")

    print("   📖 Extrayendo texto del PDF...")
    text = _extract_from_pdf(pdf_path)
    _save_cache(pdf_path, cache_path, text)
    return text


def _extract_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _cache_path(pdf_path: Path) -> Path:
    stat = pdf_path.stat()
    key = f"{pdf_path.stem}_{stat.st_size}_{int(stat.st_mtime)}"
    digest = hashlib.md5(key.encode()).hexdigest()[:12]
    return PDF_CACHE_DIR / f"{pdf_path.stem}_{digest}.txt"


def _save_cache(pdf_path: Path, cache_path: Path, text: str) -> None:
    PDF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    _cleanup_old_caches(pdf_path.stem, keep=cache_path)


def _cleanup_old_caches(stem: str, keep: Path) -> None:
    if not PDF_CACHE_DIR.exists():
        return
    for old in PDF_CACHE_DIR.glob(f"{stem}_*.txt"):
        if old != keep:
            old.unlink(missing_ok=True)


def get_book_name(pdf_path: Path) -> str:
    return pdf_path.stem

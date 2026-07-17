"""Config — Pipeline Sitio PDF."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURSORPRIME = ROOT.parent
LIBROS = CURSORPRIME / "libros a entender"
CLIENTES = CURSORPRIME / "clientes"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slug_dir(slug: str) -> Path:
    return ROOT / "data" / slug


def slug_meta(slug: str) -> Path:
    return slug_dir(slug) / "meta"


def slug_output(slug: str) -> Path:
    return slug_dir(slug) / "output"


def kdp_listing_path(producto: str) -> Path:
    return LIBROS / "resumenes" / producto / "kdp" / "amazon_listing.json"


def producto_meta_path(producto: str) -> Path:
    return LIBROS / "resumenes" / producto / "meta" / "producto.json"


def portada_imagen_path(producto: str) -> Path | None:
    """Ruta a la portada PNG del resumen PDF si existe."""
    meta = load_json(producto_meta_path(producto), {}) or {}
    rel = meta.get("imagen_portada")
    if not rel:
        return None
    path = LIBROS / "resumenes" / producto / rel
    return path if path.is_file() else None


def shopify_theme_src() -> Path:
    return CLIENTES / "vertice-pro" / "proyectos" / "shopify" / "theme"

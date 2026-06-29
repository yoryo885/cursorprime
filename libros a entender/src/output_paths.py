"""Rutas centralizadas de salida por libro."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.config import INTRO_FILENAME

META_DIR = "meta"
MAPA_DIR = "mapa"
TABLAS_DIR = "tablas"
IMAGENES_DIR = "imagenes"
HTML_DIR = "html"

MAPA_HTML = "mapa.html"
MAPA_PNG = "mapa.png"
MAPA_ESTRUCTURA = "estructura.json"
CHECKPOINT_FILENAME = ".checkpoint.json"
QUALITY_REPORT_FILENAME = "quality_report.json"
FINAL_QC_REPORT_FILENAME = "final_qc_report.json"

LEGACY_MAPA_PNG = "mapa_conceptual.png"
LEGACY_MAPA_HTML = "mapa_conceptual.html"


def meta_dir(output_dir: Path) -> Path:
    return Path(output_dir) / META_DIR


def mapa_dir(output_dir: Path) -> Path:
    return Path(output_dir) / MAPA_DIR


def tablas_dir(output_dir: Path) -> Path:
    return Path(output_dir) / TABLAS_DIR


def imagenes_dir(output_dir: Path) -> Path:
    return Path(output_dir) / IMAGENES_DIR


def html_dir(output_dir: Path) -> Path:
    return Path(output_dir) / HTML_DIR


def intro_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / INTRO_FILENAME


def intro_audiencia_path(output_dir: Path) -> Path:
    from src.config import INTRO_AUDIENCIA_FILENAME

    return meta_dir(output_dir) / INTRO_AUDIENCIA_FILENAME


def checkpoint_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / CHECKPOINT_FILENAME


def quality_report_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / QUALITY_REPORT_FILENAME


def final_qc_report_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / FINAL_QC_REPORT_FILENAME


def mapa_html_path(output_dir: Path) -> Path:
    return mapa_dir(output_dir) / MAPA_HTML


def mapa_png_path(output_dir: Path) -> Path:
    return mapa_dir(output_dir) / MAPA_PNG


def mapa_estructura_path(output_dir: Path) -> Path:
    return mapa_dir(output_dir) / MAPA_ESTRUCTURA


def resolve_intro_path(output_dir: Path) -> Path:
    nuevo = intro_path(output_dir)
    legacy = Path(output_dir) / INTRO_FILENAME
    if nuevo.exists():
        return nuevo
    if legacy.exists():
        return legacy
    return nuevo


def resolve_mapa_png(output_dir: Path) -> Optional[Path]:
    candidatos = [
        mapa_png_path(output_dir),
        Path(output_dir) / LEGACY_MAPA_PNG,
        mapa_dir(output_dir) / LEGACY_MAPA_PNG,
    ]
    for path in candidatos:
        if path.exists() and path.stat().st_size > 5000:
            return path
    return None


def resolve_mapa_estructura(output_dir: Path) -> Optional[Path]:
    nuevo = mapa_estructura_path(output_dir)
    if nuevo.exists():
        return nuevo
    return None


def ensure_book_dirs(output_dir: Path) -> None:
    for d in (meta_dir, mapa_dir, tablas_dir, imagenes_dir, html_dir):
        d(output_dir).mkdir(parents=True, exist_ok=True)

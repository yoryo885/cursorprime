"""Rutas del proyecto landing_pipeline."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src" / "skills"
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"
META = ROOT / "meta"


def slug_dir(slug: str) -> Path:
    return OUTPUT / slug


def ensure_slug(slug: str) -> Path:
    d = slug_dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    return d

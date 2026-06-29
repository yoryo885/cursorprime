"""Configuración — Centro de control prime."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
OUTPUT_DIR = ROOT / "output"
LOGS_DIR = ROOT / "logs"
CURSORPRIME = ROOT.parent
SKILLS_USER = Path.home() / ".cursor" / "skills"

PROYECTOS = {
    "analisis-de-proyectos": CURSORPRIME / "analisis-de-proyectos",
    "lluvia-de-ideas": CURSORPRIME / "lluvia-de-ideas",
    "ideas-de-proyectos": CURSORPRIME / "ideas de proyectos",
    "creador-de-prompts": CURSORPRIME / "creador de prompts",
    "creador-de-skills": CURSORPRIME / "creador de skills",
    "creador-de-contenido": CURSORPRIME / "creador de contenido",
    "project_lens": CURSORPRIME / "project_lens",
}


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

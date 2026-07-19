"""Configuración — Creador de Landings."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
DATA_DIR = ROOT / "data"
LOGS_DIR = ROOT / "logs"
TEMPLATES_DIR = ROOT / "src" / "templates"


def env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ("1", "true", "yes", "on")


CHECKPOINT_ENABLED = env_bool("CHECKPOINT", True)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:48] or "landing"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slug_dir(slug: str) -> Path:
    return DATA_DIR / slug


def slug_inputs(slug: str) -> Path:
    return slug_dir(slug) / "inputs"


def slug_meta(slug: str) -> Path:
    return slug_dir(slug) / "meta"


def slug_output(slug: str) -> Path:
    return slug_dir(slug) / "output"


def preguntas_path() -> Path:
    return META_DIR / "preguntas.json"


def constitution_path() -> Path:
    return META_DIR / "constitution.json"

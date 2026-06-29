"""Configuración del meta-proyecto ideas-de-proyectos."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDEAS_DIR = ROOT / "ideas"
EVALUACIONES_DIR = ROOT / "evaluaciones"
BORRADORES_DIR = ROOT / "borradores"
PROYECTOS_DIR = ROOT / "proyectos"
META_DIR = ROOT / "meta"
LOGS_DIR = ROOT / "logs"
PLAN_PATH = META_DIR / "plan.json"
CONSTITUTION_PATH = META_DIR / "constitution.json"

CHECKPOINT_ENABLED = True


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:48] or "proyecto"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def evaluacion_dir(slug: str) -> Path:
    return EVALUACIONES_DIR / slug


def borrador_dir(slug: str) -> Path:
    return BORRADORES_DIR / slug


def borrador_meta(slug: str) -> Path:
    return borrador_dir(slug) / "meta"


def proyecto_dir(slug: str) -> Path:
    return PROYECTOS_DIR / slug

"""Configuración — Lluvia de ideas."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
DATA_DIR = ROOT / "data"
LOGS_DIR = ROOT / "logs"
COLA_DIR = ROOT / "cola"
COLA_PENDIENTES = COLA_DIR / "pendientes"
COLA_APROBADAS = COLA_DIR / "aprobadas"
COLA_RECHAZADAS = COLA_DIR / "rechazadas"
COLA_EN_ESPERA = COLA_DIR / "en_espera"
CATEGORIAS_IDEA = ("visual", "informacion", "marketing", "nuevo_proyecto", "meta")
CURSORPRIME_ROOT = ROOT.parent
ANALISIS_ROOT = CURSORPRIME_ROOT / "analisis-de-proyectos"


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")


MOCK_FETCH = env_bool("MOCK_FETCH", True)
CHECKPOINT_ENABLED = env_bool("CHECKPOINT", True)
DEFAULT_SLUG = os.getenv("DEFAULT_SLUG", "demo_investigacion")
MAX_RESULTADOS_WEB = int(os.getenv("MAX_RESULTADOS_WEB", "8"))
MAX_RESULTADOS_YT = int(os.getenv("MAX_RESULTADOS_YT", "6"))


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:48] or "lote"


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


def slug_meta(slug: str) -> Path:
    return slug_dir(slug) / "meta"


def slug_output(slug: str) -> Path:
    return slug_dir(slug) / "output"


def constitution_path() -> Path:
    return META_DIR / "constitution.json"


def direccion_path() -> Path:
    return META_DIR / "direccion.json"


def analisis_json_path(slug: str) -> Path:
    """Análisis vive en analisis-de-proyectos/data/{slug}/"""
    p = ANALISIS_ROOT / "data" / slug / "meta" / "analisis.json"
    if p.exists():
        return p
    return slug_meta(slug) / "analisis.json"

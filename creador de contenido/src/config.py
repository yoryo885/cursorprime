"""Configuración — Creador de Contenido."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# Keys: archivo visible ELEVENLABS_KEY.env (Mac/Finder) + .env clásico
load_dotenv(ROOT / "ELEVENLABS_KEY.env")
load_dotenv(ROOT / ".env")
load_dotenv()

META_DIR = ROOT / "meta"
DATA_DIR = ROOT / "data"
LOGS_DIR = ROOT / "logs"

SALIDAS_VALIDAS = ("png", "gif", "video", "pdf")
MODULO_POR_SALIDA = {"png": "imagenes", "gif": "gifs", "video": "videos", "pdf": "pdf"}


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")


MOCK_GENERATE = env_bool("MOCK_GENERATE", True)
MOCK_KLING = env_bool("MOCK_KLING", True)
MOCK_LLM = env_bool("MOCK_LLM", True)
MOCK_TTS = env_bool("MOCK_TTS", True)
CHECKPOINT_ENABLED = env_bool("CHECKPOINT", True)
DEFAULT_SLUG = os.getenv("DEFAULT_SLUG", "demo_lote")
INTEGRACION_EXTERNA = env_bool("INTEGRACION_EXTERNA", False)
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs").strip().lower()
VIDEO_MODOS = ("slideshow", "animado")


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


def plan_path() -> Path:
    return META_DIR / "plan.json"


def constitution_path() -> Path:
    return META_DIR / "constitution.json"


def slug_dir(slug: str) -> Path:
    return DATA_DIR / slug


def slug_meta(slug: str) -> Path:
    return slug_dir(slug) / "meta"


def slug_imagenes(slug: str) -> Path:
    return slug_dir(slug) / "imagenes"


def slug_gifs(slug: str) -> Path:
    return slug_dir(slug) / "gifs"


def slug_videos(slug: str) -> Path:
    return slug_dir(slug) / "videos"


def slug_clips(slug: str) -> Path:
    return slug_dir(slug) / "videos" / "clips"


def slug_pdf(slug: str) -> Path:
    return slug_dir(slug) / "pdf"


def slug_output(slug: str) -> Path:
    return slug_dir(slug) / "output"


def normalizar_salidas(lote: dict) -> list[str]:
    if lote.get("salidas"):
        out = [s.lower() for s in lote["salidas"] if s.lower() in SALIDAS_VALIDAS]
        if out:
            return out
    legacy = (lote.get("formato") or "png").lower()
    if legacy == "mp4":
        return ["video"]
    if legacy in SALIDAS_VALIDAS:
        return [legacy]
    return ["png"]


def salidas_con_dependencias(salidas: list[str]) -> list[str]:
    """Video y PDF requieren PNG internamente."""
    s = set(salidas)
    if "video" in s or "pdf" in s or "gif" in s:
        s.add("png")
    orden = ["png", "gif", "video", "pdf"]
    return [x for x in orden if x in s]

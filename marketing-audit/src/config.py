"""Configuración — Marketing Audit."""

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
ASSETS_DIR = ROOT / "assets"
VENDOR_ROOT = ROOT.parent / "vendor" / "ai-marketing-claude"
CLIENTES_ROOT = ROOT.parent / "clientes"
AGENTS_DIR = VENDOR_ROOT / "agents"


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")


MOCK_FETCH = env_bool("MOCK_FETCH", True)
CHECKPOINT_ENABLED = env_bool("CHECKPOINT", True)
DEFAULT_SLUG = os.getenv("DEFAULT_SLUG", "demo_audit")
MAX_COMPETITORS = int(os.getenv("MAX_COMPETITORS", "5"))


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:48] or "audit"


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


def agents_meta(slug: str) -> Path:
    return slug_meta(slug) / "agents"


def constitution_path() -> Path:
    return META_DIR / "constitution.json"


def plan_path() -> Path:
    return META_DIR / "plan.json"


def branding_path() -> Path:
    return META_DIR / "report_branding.json"


def load_branding(brief: dict | None = None) -> dict:
    base = load_json(branding_path(), {}) or {}
    if not brief:
        return base
    out = {**base}
    for key in ("nombre", "whatsapp", "whatsapp_mensaje", "email", "logo"):
        if brief.get(key):
            out[key] = brief[key]
        if brief.get(f"consultor_{key}"):
            out[key] = brief[f"consultor_{key}"]
    return out

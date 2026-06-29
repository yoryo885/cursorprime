"""Configuración — Project Lens."""

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

AGENT_ORDER = [
    "context",
    "trend",
    "market",
    "competition",
    "financial",
    "scalability",
    "cost_mvp",
    "risk",
    "synthesis",
    "planner",
    "qc",
    "report",
    "improvement",
]

MVP_AGENTS = {
    "context", "financial", "cost_mvp", "synthesis", "planner", "qc", "report", "improvement"
}

AGENT_FILES = {
    "context": "context.json",
    "trend": "trend.json",
    "market": "market.json",
    "competition": "competition.json",
    "financial": "financial.json",
    "scalability": "scalability.json",
    "cost_mvp": "cost_mvp.json",
    "risk": "risk.json",
    "synthesis": "verdict.json",
    "planner": "plan_accion.json",
    "qc": "qc_result.json",
}


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")


MOCK_WEB = env_bool("MOCK_WEB", True)
CHECKPOINT_ENABLED = env_bool("CHECKPOINT", True)
DEFAULT_SLUG = os.getenv("DEFAULT_SLUG", "demo-idea")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:48] or "idea"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def constitution_path() -> Path:
    return META_DIR / "constitution.json"


def weights_path() -> Path:
    return META_DIR / "weights.json"


def plan_path() -> Path:
    return META_DIR / "plan.json"


def slug_dir(slug: str) -> Path:
    return DATA_DIR / slug


def slug_meta(slug: str) -> Path:
    return slug_dir(slug) / "meta"


def slug_output(slug: str) -> Path:
    return slug_dir(slug) / "output"


def agent_path(slug: str, agent_key: str) -> Path:
    return slug_meta(slug) / AGENT_FILES[agent_key]


def agents_for_modo(modo: str) -> list[str]:
    if modo == "mvp":
        return [a for a in AGENT_ORDER if a in MVP_AGENTS]
    return AGENT_ORDER.copy()

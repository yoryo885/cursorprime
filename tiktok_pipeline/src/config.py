"""Config — TikTok Pipeline."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SKILLS_DIR = SRC / "skills"
OUTPUT_DIR = ROOT / "output"
LOGS_DIR = ROOT / "logs"
META_DIR = ROOT / "meta"
DATA_DIR = ROOT / "data"

MOCK_LLM = os.getenv("MOCK_LLM", "true").lower() in ("1", "true", "yes", "on")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
DEFAULT_SLUG = os.getenv("DEFAULT_SLUG", "demo_pareto")

AGENT_ORDER = [
    "00_extract_fuente",
    "01_trend_research",
    "02_hook",
    "03_script",
    "04_pattern_interrupts",
    "05_onscreen_text",
    "06_cta",
    "07_loop",
    "08_audio",
    "09_caption_hashtags",
    "10_shotlist",
    "11_qa",
]

SKILL_MAP = {
    "00_extract_fuente": "extract_fuente_skill.md",
    "02_hook": "hook_skill.md",
    "03_script": "script_skill.md",
    "04_pattern_interrupts": "pattern_interrupt_skill.md",
    "05_onscreen_text": "onscreen_text_skill.md",
    "06_cta": "cta_skill.md",
    "07_loop": "loop_skill.md",
    "08_audio": "audio_skill.md",
    "09_caption_hashtags": "caption_hashtags_skill.md",
    "11_qa": "qa_checklist_skill.md",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9áéíóúñü\s_-]", "", text, flags=re.I)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:48] or "tiktok"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_skill(name: str) -> str:
    path = SKILLS_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def output_dir(slug: str) -> Path:
    return OUTPUT_DIR / slug


def checkpoint_path(slug: str) -> Path:
    return output_dir(slug) / ".checkpoint.json"

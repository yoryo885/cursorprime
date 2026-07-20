"""11a — Design tokens only (NO HTML)."""

from __future__ import annotations

import json
from typing import Any

from src.agents.base import load_skill
from src.llm_client import LLMClient


DEFAULT_TOKENS = {
    "ink": "#1b222c",
    "paper": "#f4f1ec",
    "accent": "#c9a962",
    "muted": "#7a847c",
    "sand": "#ebe6df",
    "font_heading": '"Cormorant Garamond"',
    "font_body": "Outfit",
    "radius": "0",
}


def _mock(brief: dict, _copy: dict) -> dict:
    rubro = (brief.get("rubro") or "").lower()
    tokens = dict(DEFAULT_TOKENS)
    if "tech" in rubro or "saas" in rubro:
        tokens["accent"] = "#3d7ea6"
    return tokens


def run(input: dict[str, Any]) -> dict[str, Any]:
    """Devuelve solo tokens JSON. Nunca HTML."""
    llm: LLMClient = input["llm"]
    brief = input["brief"]
    skill = load_skill("design_skill.md")
    system = (
        "Sos director de arte. Devolvés SOLO un JSON de tokens de diseño "
        "(colores, tipografía, radius). NUNCA HTML ni copy.\n\n"
        f"--- SKILL ---\n{skill}"
    )
    user = (
        f"BRIEF:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "Devolvé tokens con keys: ink, paper, accent, muted, sand, "
        "font_heading, font_body, radius."
    )
    tokens = llm.complete_json(system, user, mock_payload=_mock(brief, {}))
    # Garantizar acento único presente
    for k, v in DEFAULT_TOKENS.items():
        tokens.setdefault(k, v)
    return tokens

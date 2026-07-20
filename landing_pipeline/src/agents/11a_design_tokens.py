"""11a — Design tokens + layout variants (NO HTML)."""

from __future__ import annotations

import json
from typing import Any

from src.agents.base import load_skill
from src.llm_client import LLMClient
from src.sections import LAYOUT_DEFAULTS, LAYOUT_VARIANTS

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


def _pick_layout(brief: dict) -> dict:
    """Elige variantes de lista cerrada según tono/rubro (mock determinista)."""
    tono = (brief.get("tono") or "").lower()
    rubro = (brief.get("rubro") or "").lower()
    layout = dict(LAYOUT_DEFAULTS)
    # Editorial / educación → split + lista + comparativa (más distinto visualmente)
    if any(k in tono + " " + rubro for k in ("editorial", "educ", "libro", "profesional")):
        layout = {"hero": "split", "benefits": "lista_numerada", "pricing": "comparativa"}
    if "tech" in rubro or "saas" in rubro:
        layout = {"hero": "centrado", "benefits": "tarjetas", "pricing": "comparativa"}
    # Validar contra lista cerrada
    for sec, opts in LAYOUT_VARIANTS.items():
        if layout.get(sec) not in opts:
            layout[sec] = LAYOUT_DEFAULTS[sec]
    return layout


def _mock(brief: dict, _copy: dict) -> dict:
    tokens = dict(DEFAULT_TOKENS)
    rubro = (brief.get("rubro") or "").lower()
    if "tech" in rubro or "saas" in rubro:
        tokens["accent"] = "#3d7ea6"
    tokens["layout"] = _pick_layout(brief)
    return tokens


def run(input: dict[str, Any]) -> dict[str, Any]:
    llm: LLMClient = input["llm"]
    brief = input["brief"]
    skill = load_skill("design_skill.md")
    system = (
        "Sos director de arte. Devolvés SOLO JSON de tokens + layout. "
        "NUNCA HTML. layout.hero/benefits/pricing solo de la lista cerrada del skill.\n\n"
        f"--- SKILL ---\n{skill}\n\n"
        f"VARIANTES PERMITIDAS:\n{json.dumps(LAYOUT_VARIANTS, ensure_ascii=False)}"
    )
    user = (
        f"BRIEF:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "Devolvé: ink, paper, accent, muted, sand, font_heading, font_body, radius, "
        "layout:{hero, benefits, pricing}."
    )
    tokens = llm.complete_json(system, user, mock_payload=_mock(brief, {}))
    for k, v in DEFAULT_TOKENS.items():
        tokens.setdefault(k, v)
    layout = tokens.get("layout") or {}
    if not isinstance(layout, dict):
        layout = {}
    clean = {}
    for sec, opts in LAYOUT_VARIANTS.items():
        val = layout.get(sec) or LAYOUT_DEFAULTS[sec]
        clean[sec] = val if val in opts else LAYOUT_DEFAULTS[sec]
    tokens["layout"] = clean
    return tokens

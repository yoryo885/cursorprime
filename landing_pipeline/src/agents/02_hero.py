"""02 — Hero (incluye tiene_imagen para bloquear split sin foto)."""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.llm_client import LLMClient
from src.text_utils import propuesta, public_name


def _mock(brief: dict, _copy: dict) -> dict:
    imagen = (brief.get("imagen_hero") or "").strip()
    return {
        "titulo": _short(propuesta(brief) or f"{public_name(brief)} para tu rol", 8),
        "bajada": f"Hecho para {brief.get('publico', 'vos')}. Sin relleno.",
        "cta": brief.get("cta") or "Empezar ahora",
        "tiene_imagen": bool(imagen),
        "imagen_hero": imagen,
    }


def _short(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words])


def run(input: dict[str, Any]) -> dict[str, Any]:
    llm: LLMClient = input["llm"]
    brief = input["brief"]
    copy = input.get("copy") or {}
    # referencia.json complementa (no reemplaza) el skill
    _ref = input.get("referencia") or {}
    block = run_section(llm, "hero_skill.md", brief, copy, "hero", _mock)
    imagen = (brief.get("imagen_hero") or block.get("imagen_hero") or "").strip()
    block["tiene_imagen"] = bool(imagen)
    block["imagen_hero"] = imagen
    if _ref.get("hero_visual"):
        block["_ref_hero_visual"] = _ref["hero_visual"]
    return block

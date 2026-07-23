"""Helpers compartidos por agentes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import SKILL_MAP, load_skill
from src.llm_client import get_llm


def skill_for(agent_id: str) -> str:
    name = SKILL_MAP.get(agent_id, "")
    return load_skill(name) if name else ""


def run_with_skill(
    agent_id: str,
    user_prompt: str,
    mock_payload: dict[str, Any],
) -> dict[str, Any]:
    skill = skill_for(agent_id)
    system = (
        f"Eres el agente {agent_id} de un pipeline de TikTok.\n"
        f"Lee y obedece este skill antes de generar:\n\n{skill}"
    )
    return get_llm().complete_json(system, user_prompt, mock_payload=mock_payload)


def tema_from(state: dict) -> str:
    tema = str(state.get("tema") or "").strip()
    desde_fuente = str(state.get("tema_desde_fuente") or "").strip()
    if desde_fuente and (not tema or tema in {"desde_fuente", "productividad"}):
        return desde_fuente
    return tema or desde_fuente or str(state.get("producto") or "productividad")


def ideas_from(state: dict) -> list[str]:
    ideas = state.get("ideas_centrales") or []
    if ideas:
        return [str(x) for x in ideas]
    fe = state.get("fuente_extract") or {}
    return [str(x) for x in (fe.get("ideas_centrales") or [])]


def nicho_from(state: dict) -> str:
    return str(state.get("nicho") or "productividad personal")

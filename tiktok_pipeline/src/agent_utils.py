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
    return str(state.get("tema") or state.get("producto") or "productividad")


def nicho_from(state: dict) -> str:
    return str(state.get("nicho") or "productividad personal")

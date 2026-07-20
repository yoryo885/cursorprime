"""Base: cada agente lee su skill .md antes de generar."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from src.llm_client import LLMClient
from src.paths import SKILLS


def load_skill(name: str) -> str:
    path = SKILLS / name
    if not path.exists():
        raise FileNotFoundError(f"Skill no encontrado: {path}")
    return path.read_text(encoding="utf-8")


def run_section(
    llm: LLMClient,
    skill_file: str,
    brief: dict[str, Any],
    copy_so_far: dict[str, Any],
    section_key: str,
    mock_builder: Callable[[dict, dict], dict[str, Any]],
) -> dict[str, Any]:
    """Carga skill → system prompt → LLM/mock → bloque JSON."""
    skill = load_skill(skill_file)
    system = (
        "Sos un copywriter de landings. Seguí el skill al pie de la letra. "
        "Respondé SOLO con el JSON del 'Output esperado'. Idioma: español.\n\n"
        f"--- SKILL ---\n{skill}"
    )
    user = (
        f"BRIEF:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"COPY YA GENERADO:\n{json.dumps(copy_so_far, ensure_ascii=False, indent=2)}\n\n"
        f"Generá el bloque '{section_key}'."
    )
    mock = mock_builder(brief, copy_so_far)
    return llm.complete_json(system, user, mock_payload=mock)

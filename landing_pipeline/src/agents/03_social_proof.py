"""03 — Social proof"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.llm_client import LLMClient


def _mock(brief: dict, _copy: dict) -> dict:
    n = brief.get("n_productos") or 1
    r = brief.get("n_roles") or 1
    return {
        "cifra_o_logos": f"{n} productos · {r} perfiles",
        "texto": "Colección lista para aplicar",
        "confianza": "media",
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    llm: LLMClient = input["llm"]
    return run_section(
        llm, "social_proof_skill.md", input["brief"], input.get("copy") or {}, "social_proof", _mock
    )

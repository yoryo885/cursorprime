"""03 — Social proof (dato verificable; no inventar estrellas)"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.llm_client import LLMClient


def _mock(brief: dict, _copy: dict) -> dict:
    extras = brief.get("extras") or {}
    # Preferir prueba social real si el brief la trae
    real = brief.get("social_proof") or extras.get("social_proof") or {}
    if real.get("cifra_o_logos") or real.get("rating"):
        return {
            "cifra_o_logos": real.get("cifra_o_logos") or real.get("rating"),
            "texto": real.get("texto") or "",
            "confianza": "alta",
            "fuente": real.get("fuente") or "brief",
        }
    n = brief.get("n_productos") or 1
    r = brief.get("n_roles") or 1
    return {
        "cifra_o_logos": f"{n} productos · {r} perfiles",
        "texto": "Dato del catálogo · sin reseñas inventadas",
        "confianza": "media",
        "fuente": "producto",
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    llm: LLMClient = input["llm"]
    return run_section(
        llm, "social_proof_skill.md", input["brief"], input.get("copy") or {}, "social_proof", _mock
    )

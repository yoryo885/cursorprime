"""04 — Problem"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    publico = brief.get("publico") or "profesionales"
    return {
        "headline": "Sabés la teoría… y el día a día no cambia",
        "dolores": [
            f"Leés libros útiles pero no llegan a tu rol como {publico}.",
            "Perdés tiempo buscando el 20% que importa.",
            "Los resúmenes genéricos no hablan tu lenguaje.",
        ],
        "puente": f"Por eso {brief.get('nombre_producto') or brief.get('marca')} traduce métodos clásicos a tu oficio.",
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "problem_skill.md",
        input["brief"],
        input.get("copy") or {},
        "problem",
        _mock,
    )

"""07 — Pricing"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    return {
        "precio": brief.get("precio") or "Consultar",
        "incluye": [
            "Acceso / descarga inmediata",
            "Formato profesional listo para usar",
            "Soporte de lanzamiento de colección",
        ],
        "cta": brief.get("cta") or "Comprar ahora",
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "pricing_skill.md",
        input["brief"],
        input.get("copy") or {},
        "pricing",
        _mock,
    )

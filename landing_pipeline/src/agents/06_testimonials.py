"""06 — Testimonials (no inventar; omitir si no hay data)"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    real = brief.get("testimonios") or (brief.get("extras") or {}).get("testimonios") or []
    if real:
        return {"omitida": False, "items": real[:3], "motivo": ""}
    return {
        "omitida": True,
        "motivo": "sin testimonios reales en el brief",
        "items": [],
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "testimonials_skill.md",
        input["brief"],
        input.get("copy") or {},
        "testimonials",
        _mock,
    )

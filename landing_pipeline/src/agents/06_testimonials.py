"""06 — Testimonials (no inventar)"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    extras = brief.get("extras") or {}
    real = extras.get("testimonios") or []
    if real:
        return {"items": real[:3], "nota": ""}
    return {"items": [], "nota": "sin testimonios reales"}


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "testimonials_skill.md",
        input["brief"],
        input.get("copy") or {},
        "testimonials",
        _mock,
    )

"""09 — CTA final"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, copy: dict) -> dict:
    hero = copy.get("hero") or {}
    return {
        "headline": hero.get("titulo") or brief.get("promesa") or "Empezá hoy",
        "sub": hero.get("bajada") or f"Elegí {brief.get('producto')} y aplicá esta semana.",
        "cta": hero.get("cta") or brief.get("cta") or "Ver oferta",
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "cta_skill.md",
        input["brief"],
        input.get("copy") or {},
        "cta_final",
        _mock,
    )

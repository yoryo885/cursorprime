"""10 — Footer"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    return {
        "marca": brief.get("marca") or "",
        "contacto": brief.get("contacto") or "hola@ejemplo.com",
        "legales": ["Privacidad", "Términos"],
        "redes": (brief.get("extras") or {}).get("redes") or [],
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "footer_skill.md",
        input["brief"],
        input.get("copy") or {},
        "footer",
        _mock,
    )

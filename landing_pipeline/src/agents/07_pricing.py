"""07 — Pricing (sin duplicar 'desde')"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.text_utils import sanitize_prepend


def _mock(brief: dict, _copy: dict) -> dict:
    raw = (brief.get("precio") or "Consultar").strip()
    # Si el brief ya trae "desde", no anteponer otra vez
    precio = sanitize_prepend("desde", raw) if raw.lower() not in ("consultar",) else raw
    # Si raw ya era "desde $4.99", sanitize lo deja igual
    if raw.lower().startswith("desde"):
        precio = raw
    return {
        "precio": precio,
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

"""07 — Pricing (sin duplicar 'desde' + garantía bajo el CTA)"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.text_utils import sanitize_prepend


def _mock(brief: dict, _copy: dict) -> dict:
    raw = (brief.get("precio") or "Consultar").strip()
    if raw.lower().startswith("desde"):
        precio = raw
    elif raw.lower() in ("consultar",):
        precio = raw
    else:
        precio = sanitize_prepend("desde", raw)
    garantia = (
        brief.get("garantia")
        or (brief.get("extras") or {}).get("garantia")
        or "Pago único · acceso inmediato · sin letra chica"
    )
    return {
        "precio": precio,
        "incluye": [
            "Acceso / descarga inmediata",
            "Formato profesional listo para usar",
            "Soporte de lanzamiento de colección",
        ],
        "cta": brief.get("cta") or "Comprar ahora",
        "garantia": garantia,
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

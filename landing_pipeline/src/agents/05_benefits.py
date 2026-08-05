"""05 — Benefits"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.text_utils import sanitize_prepend


def _mock(brief: dict, _copy: dict) -> dict:
    precio = (brief.get("precio") or "").strip()
    if precio:
        # Nunca: "Empezás desde" + "desde $4.99"
        precio_txt = sanitize_prepend("desde", precio)
        precio_item = {
            "titulo": "Precio de entrada real",
            "texto": f"Empezás {precio_txt}.",
        }
    else:
        precio_item = {
            "titulo": "Precio de entrada real",
            "texto": "Precio claro, sin letra chica.",
        }
    return {
        "items": [
            {
                "titulo": "Hecho para tu oficio",
                "texto": f"Ejemplos y prioridades de {brief.get('publico', 'tu rol')}, no teoría genérica.",
            },
            {
                "titulo": "Método claro en semanas",
                "texto": "Sabés qué hacer cada semana, sin relleno ni moda.",
            },
            {
                "titulo": "Formato listo para usar",
                "texto": "PDF profesional: ordenado, descargable, aplicable hoy.",
            },
            precio_item,
        ]
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "benefits_skill.md",
        input["brief"],
        input.get("copy") or {},
        "benefits",
        _mock,
    )

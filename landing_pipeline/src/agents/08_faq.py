"""08 — FAQ"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
    marca = brief.get("marca")
    producto = brief.get("producto")
    publico = brief.get("publico")
    return {
        "items": [
            {
                "q": f"¿Qué es {producto}?",
                "a": f"Una oferta de {marca} pensada para {publico}: clara, aplicable y sin relleno.",
            },
            {
                "q": "¿Para quién es?",
                "a": f"Para {publico} que quieren método práctico, no teoría genérica.",
            },
            {
                "q": "¿Cómo lo recibo?",
                "a": "Acceso digital inmediato tras la compra (PDF / descarga según el producto).",
            },
            {
                "q": "¿En qué se diferencia de un resumen genérico?",
                "a": "Está escrito para tu rol: lenguaje, ejemplos y prioridades de tu día a día.",
            },
            {
                "q": f"¿Cuánto cuesta?",
                "a": f"{brief.get('precio') or 'El precio está visible en la sección de compra.'} Sin letra chica.",
            },
        ]
    }


def run(input: dict[str, Any]) -> dict[str, Any]:
    return run_section(
        input["llm"],
        "faq_skill.md",
        input["brief"],
        input.get("copy") or {},
        "faq",
        _mock,
    )

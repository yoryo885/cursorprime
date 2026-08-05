"""08 — FAQ (nombre_producto + garantía/riesgo)"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section
from src.text_utils import public_name


def _mock(brief: dict, _copy: dict) -> dict:
    nombre = public_name(brief)
    publico = brief.get("publico")
    return {
        "items": [
            {
                "q": f"¿Qué es {nombre}?",
                "a": f"{nombre} ofrece guías prácticas para {publico}: claras, aplicables y sin relleno.",
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
                "q": "¿Qué pasa si no me sirve?",
                "a": "Escribimos y te ayudamos. Queremos que te sirva en tu oficio — sin letra chica escondida.",
            },
            {
                "q": "¿Cuánto cuesta?",
                "a": f"{brief.get('precio') or 'El precio está visible en la sección de compra.'} Pago único, sin suscripción.",
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

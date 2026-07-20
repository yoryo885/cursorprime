"""05 — Benefits"""

from __future__ import annotations

from typing import Any

from src.agents.base import run_section


def _mock(brief: dict, _copy: dict) -> dict:
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
            {
                "titulo": "Precio de entrada real",
                "texto": f"Empezás desde {brief.get('precio') or 'un precio accesible'}.",
            },
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

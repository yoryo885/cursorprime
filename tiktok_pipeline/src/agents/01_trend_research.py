"""01 — Research de tendencias / formatos (mock o heurística)."""

from __future__ import annotations

from typing import Any

from src.agent_utils import nicho_from, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    trend: dict[str, Any] = {
        "tema": tema,
        "nicho": nicho,
        "formatos_sugeridos": [
            "talking-head + texto grande",
            "lista 3 pasos con cortes rápidos",
            "contrarian opener + prueba",
        ],
        "sonidos_sugeridos": [
            {"tipo": "voz_off", "nota": "voz clara, ritmo medio"},
            {"tipo": "trend", "nota": "buscar sonido trending del nicho (no archivo fijo)"},
        ],
        "angulos": [
            f"Lo que nadie te dice de {tema}",
            f"Deja de hacer X con {tema}",
            f"3 pasos para aplicar {tema} hoy",
        ],
        "confidence": "low",
        "fuente": "mock_heuristica",
    }
    return {"trend": trend}

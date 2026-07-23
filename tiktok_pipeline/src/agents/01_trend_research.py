"""01 — Research de tendencias / formatos (mock o heurística)."""

from __future__ import annotations

from typing import Any

from src.agent_utils import nicho_from, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    ideas = list(input.get("ideas_centrales") or [])
    angulos = []
    if ideas:
        angulos.append(f"Nadie aplica esto de «{ideas[0][:60]}…»" if len(ideas[0]) > 60 else f"Nadie aplica esto: {ideas[0]}")
        if len(ideas) > 1:
            angulos.append(f"El error con {tema}: ignorar que {ideas[1][:70]}")
        angulos.append(f"3 ideas de {tema} que cambian tu {nicho}")
    else:
        angulos = [
            f"Lo que nadie te dice de {tema}",
            f"Deja de hacer X con {tema}",
            f"3 pasos para aplicar {tema} hoy",
        ]
    trend: dict[str, Any] = {
        "tema": tema,
        "nicho": nicho,
        "ideas_usadas": ideas[:5],
        "formatos_sugeridos": [
            "talking-head + texto grande",
            "lista 3 pasos con cortes rápidos",
            "contrarian opener + prueba",
        ],
        "sonidos_sugeridos": [
            {"tipo": "voz_off", "nota": "voz clara, ritmo medio"},
            {"tipo": "trend", "nota": "buscar sonido trending del nicho (no archivo fijo)"},
        ],
        "angulos": angulos[:3],
        "confidence": "medium" if ideas else "low",
        "fuente": "ideas_centrales" if ideas else "mock_heuristica",
    }
    return {"trend": trend}

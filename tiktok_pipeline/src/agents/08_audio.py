"""08 — Audio sugerido."""

from __future__ import annotations

from src.agent_utils import run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    trend = input.get("trend") or {}
    mock = {
        "tipo": "mix",
        "ritmo": "medio",
        "nota": "Voz en off clara + música de fondo suave; cortes al ritmo de los pasos.",
        "sugerencia_busqueda": f"voz off productividad / {tema} beat medio",
        "desde_trend": (trend.get("sonidos_sugeridos") or [])[:2],
    }
    user = f"Script: {input.get('script')}\nSugiere audio."
    data = run_with_skill("08_audio", user, mock)
    return {"audio": data}

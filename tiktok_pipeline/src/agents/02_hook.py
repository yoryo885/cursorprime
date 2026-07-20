"""02 — Hook (3 variantes)."""

from __future__ import annotations

from src.agent_utils import nicho_from, run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    trend = input.get("trend") or {}
    angulos = trend.get("angulos") or []
    mock = {
        "hook": angulos[0] if angulos else f"Nadie te dice esto sobre {tema}",
        "variante_2": angulos[1] if len(angulos) > 1 else f"Dejé de complicar {tema}. Resultado brutal.",
        "variante_3": angulos[2] if len(angulos) > 2 else f"Si {tema} te abruma, mira esto 3 segundos.",
    }
    user = f"Tema: {tema}\nNicho: {nicho}\nTrend: {trend}\nGenera 3 hooks."
    data = run_with_skill("02_hook", user, mock)
    return {"hooks": data, "hook_elegido": data.get("hook", "")}

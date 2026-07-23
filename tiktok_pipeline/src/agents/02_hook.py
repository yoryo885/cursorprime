"""02 — Hook (3 variantes)."""

from __future__ import annotations

from src.agent_utils import nicho_from, run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    trend = input.get("trend") or {}
    ideas = list(input.get("ideas_centrales") or [])
    angulos = trend.get("angulos") or []
    idea0 = ideas[0] if ideas else ""
    mock = {
        "hook": angulos[0] if angulos else (
            f"Nadie te dice esto: {idea0[:70]}" if idea0 else f"Nadie te dice esto sobre {tema}"
        ),
        "variante_2": angulos[1] if len(angulos) > 1 else (
            f"Dejé de ignorar el 20% en {nicho}. Cambió todo." if ideas else f"Dejé de complicar {tema}. Resultado brutal."
        ),
        "variante_3": angulos[2] if len(angulos) > 2 else f"Si {tema} te abruma, mira esto 3 segundos.",
    }
    user = (
        f"Tema: {tema}\nNicho: {nicho}\nTrend: {trend}\n"
        f"Ideas centrales (pescadas de la fuente, solo lectura):\n- "
        + "\n- ".join(ideas or ["(sin fuente)"])
        + "\nGenera 3 hooks basados en esas ideas, no inventes un libro nuevo."
    )
    data = run_with_skill("02_hook", user, mock)
    return {"hooks": data, "hook_elegido": data.get("hook", "")}

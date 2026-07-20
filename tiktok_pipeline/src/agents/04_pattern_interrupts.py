"""04 — Pattern interrupts."""

from __future__ import annotations

from src.agent_utils import run_with_skill


def run(input: dict) -> dict:
    script = input.get("script") or {}
    dur = int(script.get("duracion_seg_aprox") or 35)
    mock = {
        "interrupts": [
            {"t_inicio": 0, "t_fin": 2, "tipo": "zoom_in", "nota": "cara + hook"},
            {"t_inicio": 2, "t_fin": 5, "tipo": "texto_pop", "nota": "refuerzo hook"},
            {"t_inicio": 5, "t_fin": 8, "tipo": "corte", "nota": "paso 1"},
            {"t_inicio": 8, "t_fin": 12, "tipo": "b-roll", "nota": "lista / pantalla"},
            {"t_inicio": 12, "t_fin": 16, "tipo": "angle_change", "nota": "paso 2"},
            {"t_inicio": 16, "t_fin": 20, "tipo": "zoom_out", "nota": "gesto cortar"},
            {"t_inicio": 20, "t_fin": 26, "tipo": "corte", "nota": "paso 3"},
            {"t_inicio": 26, "t_fin": 30, "tipo": "texto_pop", "nota": "CTA setup"},
            {"t_inicio": 30, "t_fin": min(dur, 35), "tipo": "zoom_in", "nota": "loop + CTA"},
        ]
    }
    user = f"Script: {script}\nMarca pattern interrupts cada 2-3s."
    data = run_with_skill("04_pattern_interrupts", user, mock)
    return {"pattern_interrupts": data}

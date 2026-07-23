"""05 — Texto en pantalla."""

from __future__ import annotations

from src.agent_utils import run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    script = input.get("script") or {}
    bloques = script.get("bloques") or []
    textos = [
        {"escena_id": 0, "texto": "Nadie te lo dice", "t_inicio": 0, "t_fin": 3},
    ]
    t = 5
    defaults = ["Marca el 20%", "Corta el resto", "Protege el foco"]
    for i, b in enumerate(bloques[:3]):
        textos.append(
            {
                "escena_id": b.get("id", i + 1),
                "texto": defaults[i] if i < len(defaults) else f"Paso {i+1}",
                "t_inicio": t,
                "t_fin": t + 4,
            }
        )
        t += 7
    textos.append({"escena_id": 99, "texto": f"Aplica {tema[:18]}", "t_inicio": t, "t_fin": t + 4})
    mock = {"textos": textos}
    user = f"Script: {script}\nGenera textos en pantalla."
    data = run_with_skill("05_onscreen_text", user, mock)
    return {"onscreen_text": data}

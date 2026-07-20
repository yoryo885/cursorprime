"""03 — Script / desarrollo."""

from __future__ import annotations

from src.agent_utils import nicho_from, run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    hook = input.get("hook_elegido") or (input.get("hooks") or {}).get("hook", "")
    mock = {
        "mensaje_central": f"Con {tema}, el 20% de acciones mueve el 80% del resultado.",
        "bloques": [
            {
                "id": 1,
                "texto": f"Paso 1: lista todo lo que haces en {nicho} y marca solo lo que mueve números.",
            },
            {
                "id": 2,
                "texto": "Paso 2: corta o delega el resto esta semana. Sin culpa.",
            },
            {
                "id": 3,
                "texto": "Paso 3: protege 90 minutos diarios para ese 20%. Ahí está el salto.",
            },
        ],
        "duracion_seg_aprox": 35,
        "hook_usado": hook,
    }
    user = f"Hook: {hook}\nTema: {tema}\nNicho: {nicho}\nEscribe el desarrollo."
    data = run_with_skill("03_script", user, mock)
    return {"script": data}

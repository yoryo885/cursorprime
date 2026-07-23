"""07 — Loop final."""

from __future__ import annotations

from src.agent_utils import run_with_skill


def run(input: dict) -> dict:
    hook = input.get("hook_elegido") or (input.get("hooks") or {}).get("hook", "")
    mock = {
        "loop": "Y eso… nadie te lo dice en serio.",
        "conexion_con_hook": hook,
    }
    user = f"Hook: {hook}\nEscribe el loop final que conecte."
    data = run_with_skill("07_loop", user, mock)
    return {"loop": data}

"""06 — CTA."""

from __future__ import annotations

from src.agent_utils import run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    palabra = "".join(ch for ch in tema.upper() if ch.isalnum())[:12] or "GUIA"
    mock = {
        "cta": f"Comenta {palabra} y te paso el checklist",
        "accion": "comentar",
        "palabra_clave": palabra,
    }
    user = f"Tema: {tema}\nHook: {input.get('hook_elegido')}\nUna sola CTA."
    data = run_with_skill("06_cta", user, mock)
    return {"cta": data}

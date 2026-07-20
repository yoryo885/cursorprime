"""09 — Caption + hashtags."""

from __future__ import annotations

from src.agent_utils import nicho_from, run_with_skill, tema_from


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    hook = input.get("hook_elegido") or ""
    cta = (input.get("cta") or {}).get("cta", "")
    tag_nicho = "#" + "".join(ch for ch in nicho.lower() if ch.isalnum())[:18]
    mock = {
        "caption": f"El truco no es hacer más con {tema}. Es soltar el 80% que no mueve.\n{cta}",
        "hashtags": [tag_nicho or "#productividad", "#enfoque", "#pareto", "#guias"],
    }
    # filtrar genéricos
    ban = {"#fyp", "#viral", "#parati", "#foryou"}
    mock["hashtags"] = [h for h in mock["hashtags"] if h.lower() not in ban][:5]
    user = f"Hook: {hook}\nTema: {tema}\nCTA: {cta}\nCaption + hashtags de nicho."
    data = run_with_skill("09_caption_hashtags", user, mock)
    return {"caption_hashtags": data}

"""03 — Script / desarrollo a partir de ideas centrales."""

from __future__ import annotations

from src.agent_utils import nicho_from, run_with_skill, tema_from


def _acortar(texto: str, max_len: int = 140) -> str:
    t = " ".join(str(texto).split())
    # Quita muletillas de resumen editorial
    for pref in ("Verás que ", "Notarás que ", "Descubrirás que ", "Comprenderás que ", "Reconocerás que ", "Observarás que ", "Encontrarás que "):
        if t.startswith(pref):
            t = t[len(pref):]
            t = t[0].upper() + t[1:] if t else t
            break
    if len(t) <= max_len:
        return t
    cut = t[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"


def run(input: dict) -> dict:
    tema = tema_from(input)
    nicho = nicho_from(input)
    hook = input.get("hook_elegido") or (input.get("hooks") or {}).get("hook", "")
    ideas = list(input.get("ideas_centrales") or [])
    ideas_cortas = [_acortar(i) for i in ideas[:5]]

    if len(ideas_cortas) >= 3:
        bloques = [
            {"id": 1, "texto": f"Uno: {ideas_cortas[0]}"},
            {"id": 2, "texto": f"Dos: {ideas_cortas[1]}"},
            {"id": 3, "texto": f"Tres: {ideas_cortas[2]}"},
        ]
        mensaje = ideas_cortas[0]
    elif ideas_cortas:
        bloques = [{"id": i + 1, "texto": f"{i+1}. {t}"} for i, t in enumerate(ideas_cortas[:3])]
        while len(bloques) < 3:
            n = len(bloques) + 1
            bloques.append({"id": n, "texto": f"{n}. Aplícalo hoy en tu {nicho}."})
        mensaje = ideas_cortas[0]
    else:
        bloques = [
            {"id": 1, "texto": f"Paso 1: lista todo lo que haces en {nicho} y marca solo lo que mueve números."},
            {"id": 2, "texto": "Paso 2: corta o delega el resto esta semana. Sin culpa."},
            {"id": 3, "texto": "Paso 3: protege 90 minutos diarios para ese 20%. Ahí está el salto."},
        ]
        mensaje = f"Con {tema}, el 20% de acciones mueve el 80% del resultado."

    mock = {
        "mensaje_central": mensaje,
        "bloques": bloques,
        "duracion_seg_aprox": 35,
        "hook_usado": hook,
        "origen": "ideas_centrales" if ideas else "tema",
        "ideas_usadas": ideas_cortas[:3],
    }
    user = (
        f"Hook: {hook}\nTema: {tema}\nNicho: {nicho}\n"
        f"Ideas centrales de la fuente (transformar en guion hablado corto, no copiar el PDF):\n- "
        + "\n- ".join(ideas_cortas or ["(sin fuente — usa tema)"])
        + "\nEscribe el desarrollo en 3 pasos."
    )
    data = run_with_skill("03_script", user, mock)
    return {"script": data}

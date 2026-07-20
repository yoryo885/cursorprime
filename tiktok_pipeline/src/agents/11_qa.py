"""11 — QA contra checklist."""

from __future__ import annotations

from src.agent_utils import run_with_skill


def run(input: dict) -> dict:
    issues = []
    regenerar = []

    hook = (input.get("hook_elegido") or "").lower()
    if any(hook.startswith(x) for x in ("hola", "hoy les", "qué tal", "buenas")):
        issues.append({"agente": "02_hook", "detalle": "Hook suena a saludo/intro"})
        regenerar.append("02_hook")

    script = input.get("script") or {}
    if not script.get("mensaje_central"):
        issues.append({"agente": "03_script", "detalle": "Falta mensaje central"})
        regenerar.append("03_script")
    if len(script.get("bloques") or []) < 3:
        issues.append({"agente": "03_script", "detalle": "Menos de 3 bloques"})
        regenerar.append("03_script")

    textos = (input.get("onscreen_text") or {}).get("textos") or []
    if not textos:
        issues.append({"agente": "05_onscreen_text", "detalle": "Sin texto en pantalla"})
        regenerar.append("05_onscreen_text")

    interrupts = (input.get("pattern_interrupts") or {}).get("interrupts") or []
    if len(interrupts) < 4:
        issues.append({"agente": "04_pattern_interrupts", "detalle": "Pocos cortes (riesgo plano fijo)"})
        regenerar.append("04_pattern_interrupts")
    else:
        # huecos > 5s
        sorted_i = sorted(interrupts, key=lambda x: x.get("t_inicio", 0))
        for a, b in zip(sorted_i, sorted_i[1:]):
            gap = (b.get("t_inicio", 0) - a.get("t_fin", 0))
            if gap > 5:
                issues.append(
                    {
                        "agente": "04_pattern_interrupts",
                        "detalle": f"Hueco {gap}s sin interrupt ({a.get('t_fin')}→{b.get('t_inicio')})",
                    }
                )
                regenerar.append("04_pattern_interrupts")
                break

    cta = input.get("cta") or {}
    if not cta.get("cta"):
        issues.append({"agente": "06_cta", "detalle": "CTA ausente"})
        regenerar.append("06_cta")

    loop = input.get("loop") or {}
    if not loop.get("loop"):
        issues.append({"agente": "07_loop", "detalle": "Loop ausente"})
        regenerar.append("07_loop")

    tags = [t.lower() for t in (input.get("caption_hashtags") or {}).get("hashtags") or []]
    if any(t in {"#fyp", "#viral", "#parati", "#foryou"} for t in tags):
        issues.append({"agente": "09_caption_hashtags", "detalle": "Hashtags genéricos prohibidos"})
        regenerar.append("09_caption_hashtags")

    if not input.get("shotlist_md"):
        issues.append({"agente": "10_shotlist", "detalle": "Sin shotlist"})
        regenerar.append("10_shotlist")

    # score
    penalty = 12 * len({i["agente"] for i in issues})
    score = max(0, 100 - penalty)
    mock = {
        "score": score,
        "ok": score >= 70 and not regenerar,
        "issues": issues,
        "regenerar": sorted(set(regenerar)),
    }
    user = f"Revisa este guion acumulado: hooks={input.get('hooks')}, script={script}, cta={cta}, loop={loop}"
    data = run_with_skill("11_qa", user, mock)
    # Prefer local deterministic QA over LLM hallucination in mock
    if not issues:
        data = mock
    else:
        data = {**mock, **{k: data.get(k, mock[k]) for k in ()}}
        data = mock
    return {"qa": data}

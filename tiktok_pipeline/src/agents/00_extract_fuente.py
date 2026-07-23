"""00 — Extrae ideas centrales de una fuente (resumen/PDF) en solo lectura."""

from __future__ import annotations

from src.fuente import extract_ideas
from src.llm_client import get_llm
from src.config import load_skill


def run(input: dict) -> dict:
    fuente_path = str(input.get("fuente") or input.get("fuente_path") or "")
    base = extract_ideas(fuente_path)

    # Opcional: con LLM real, refinar a 3–5 ideas; mock = heurística del extractor
    skill = load_skill("extract_fuente_skill.md")
    if fuente_path and base.get("ideas_centrales") and not get_llm().mock:
        user = (
            f"Fuente (solo lectura): {base.get('titulo_fuente')}\n"
            f"Ideas crudas:\n- " + "\n- ".join(base["ideas_centrales"]) + "\n"
            "Devuelve JSON con ideas_centrales (3 a 5 frases cortas para video TikTok)."
        )
        refined = get_llm().complete_json(
            f"Obedece este skill:\n{skill}",
            user,
            mock_payload=base,
        )
        if refined.get("ideas_centrales"):
            base["ideas_centrales"] = list(refined["ideas_centrales"])[:7]
            base["extracto_corto"] = " | ".join(base["ideas_centrales"][:3])
            base["confidence"] = refined.get("confidence") or base["confidence"]

    out = {"fuente_extract": base, "ideas_centrales": base.get("ideas_centrales") or []}
    # Si hay título en la fuente y el tema es genérico, enriquecer tema
    if base.get("titulo_fuente") and not input.get("tema_fijo"):
        out["tema_desde_fuente"] = base["titulo_fuente"]
    return out

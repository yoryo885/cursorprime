"""Entrevista: interactiva o desde defaults/archivo."""

from __future__ import annotations

import sys
from pathlib import Path

from src.config import load_json, preguntas_path, save_json, slug_inputs


DEMO_RESPUESTAS = {
    "idea": "Tienda de guías PDF por oficio, look colección tipo Filjós",
    "marca": "Vértice Pro",
    "producto": "Guías PDF para tu rol profesional",
    "cliente": "Profesionales por oficio (psicopedagogas, docentes, abogados…)",
    "promesa": "Ideas de libros aplicadas a tu rol — elige tu guía",
    "catalogo": "si — catálogo default libro×rol",
    "cta": "Ver colección",
    "precio": "desde $4.99",
    "tono": "editorial",
    "estilo": "tienda",
    "estilo_preferido": "tienda",
    "clima_color": "auto",
    "paleta": "auto",
    "referencia": "https://filjos.com/",
    "extra": "filtros por rol + newsletter",
    "_cliente_demo": True,
}


def run_interview(slug: str, interactive: bool = True, prefill: dict | None = None) -> dict:
    spec = load_json(preguntas_path(), {}) or {}
    preguntas = spec.get("preguntas") or []
    answers = dict(prefill or {})

    print(f"\n{spec.get('titulo', 'Brief landing')}")
    print(spec.get("intro", ""))
    print()

    for q in preguntas:
        qid = q["id"]
        if answers.get(qid):
            print(f"  · {q['texto']}\n    → {answers[qid]} (ya definido)")
            continue
        ejemplo = q.get("ejemplo", "")
        prompt = f"  {q['texto']}"
        if ejemplo:
            prompt += f"\n    ej: {ejemplo}"
        prompt += "\n  > "
        if interactive and sys.stdin.isatty():
            val = input(prompt).strip()
            answers[qid] = val or ejemplo
        else:
            answers[qid] = ejemplo
            print(f"  · {q['texto']}\n    → {answers[qid]} (default)")

    dest = slug_inputs(slug) / "respuestas.json"
    save_json(dest, answers)
    print(f"\n✅ Respuestas → {dest}\n")
    return answers


def load_or_interview(slug: str, interactive: bool = False, force: bool = False) -> dict:
    path = slug_inputs(slug) / "respuestas.json"
    if path.exists() and not force:
        return load_json(path, {}) or {}
    return run_interview(slug, interactive=interactive)

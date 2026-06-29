#!/usr/bin/env python3
"""Enrutador automático cursorprime — intención → skill + prompt + pipeline."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUTER_PATH = ROOT / "meta" / "router.json"
SKILLS_DIR = Path.home() / ".cursor" / "skills"


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def score_route(text: str, route: dict) -> int:
    match = route.get("match") or {}
    any_kw = [normalize(k) for k in match.get("any", [])]
    none_kw = [normalize(k) for k in match.get("none", [])]

    for kw in none_kw:
        if kw and kw in text:
            return -1

    hits = sum(1 for kw in any_kw if kw and kw in text)
    if not any_kw:
        return -1
    if hits == 0:
        return -1

    return hits * 10 + int(route.get("priority", 0))


def route_text(texto: str, router: dict | None = None) -> dict:
    router = router or json.loads(ROUTER_PATH.read_text(encoding="utf-8"))
    norm = normalize(texto)

    best: dict | None = None
    best_score = -1

    for route in router.get("routes", []):
        s = score_route(norm, route)
        if s > best_score:
            best_score = s
            best = route

    if not best:
        return {
            "matched": False,
            "texto": texto,
            **router.get("fallback", {}),
        }

    skill = best.get("skill")
    skill_path = SKILLS_DIR / skill / "SKILL.md" if skill else None

    return {
        "matched": True,
        "texto": texto,
        "route_id": best.get("id"),
        "score": best_score,
        "skill": skill,
        "skill_path": str(skill_path) if skill_path and skill_path.exists() else None,
        "proyecto": best.get("proyecto"),
        "prompt": best.get("prompt"),
        "pipeline": best.get("pipeline"),
        "nota": best.get("nota"),
        "acciones": _build_actions(best, texto),
    }


def _build_actions(route: dict, texto: str) -> list[str]:
    actions: list[str] = []
    prompt = route.get("prompt") or {}
    slug = re.sub(r"[^a-z0-9_]+", "_", normalize(texto))[:32] or "lote"

    if prompt.get("auto"):
        actions.append(
            "cd 'creador de prompts' && "
            f"python3 creador_prompts_main.py --tipo {prompt['tipo']} "
            f"--proyecto {prompt['proyecto_destino']} --slug {slug}"
        )

    pipeline = route.get("pipeline")
    if pipeline:
        cmd = pipeline["cmd"].format(slug=slug, texto=texto.replace('"', '\\"'))
        actions.append(f"cd '{pipeline['cwd']}' && {cmd}")

    skill = route.get("skill")
    if skill:
        actions.insert(0, f"Leer ~/.cursor/skills/{skill}/SKILL.md y ejecutar flujo")

    return actions


def main() -> None:
    p = argparse.ArgumentParser(description="Router cursorprime")
    p.add_argument("--texto", required=True, help="Mensaje del usuario a enrutar")
    p.add_argument("--json", action="store_true", help="Salida JSON")
    args = p.parse_args()

    result = route_text(args.texto)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not result.get("matched"):
        print(f"❓ Sin ruta clara para: {args.texto!r}")
        print(result.get("mensaje", ""))
        sys.exit(1)

    print(f"🎯 Ruta: {result['route_id']} (score {result['score']})")
    print(f"   Skill:  {result['skill']}")
    if result.get("prompt"):
        pr = result["prompt"]
        auto = "auto" if pr.get("auto") else "manual"
        print(f"   Prompt: tipo={pr.get('tipo')} → {pr.get('proyecto_destino')} ({auto})")
    print(f"   Proyecto: {result['proyecto']}")
    if result.get("nota"):
        print(f"   Nota: {result['nota']}")
    print("\nAcciones:")
    for i, a in enumerate(result.get("acciones", []), 1):
        print(f"  {i}. {a}")


if __name__ == "__main__":
    main()

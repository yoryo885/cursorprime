#!/usr/bin/env python3
"""Evaluador de proyectos — punto de entrada."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import IDEAS_DIR, evaluacion_dir, load_json, save_json, slugify  # noqa: E402
from src.evaluator import evaluate, render_informe  # noqa: E402


def load_idea(path: Path | None, texto: str | None) -> tuple[dict, str]:
    if texto:
        slug = slugify(texto[:50])
        return {"titulo": texto[:60], "problema": texto}, slug
    if path:
        if path.suffix == ".json":
            idea = load_json(path, {}) or {}
        else:
            idea = {"titulo": path.stem, "problema": path.read_text(encoding="utf-8")}
        slug = str(idea.get("slug") or "").strip() or slugify(
            str(idea.get("titulo") or path.stem)
        )
        return idea, slug
    raise SystemExit("Indica ideas/archivo.json o --texto")


def cmd_evaluar(args: argparse.Namespace) -> None:
    path = Path(args.idea_file) if args.idea_file else None
    idea, slug = load_idea(path, args.texto)
    if args.slug:
        slug = args.slug

    result = evaluate(idea, slug)
    out_dir = evaluacion_dir(slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    veredicto_path = out_dir / "veredicto.json"
    informe_path = out_dir / "informe.md"
    save_json(veredicto_path, result)
    informe_path.write_text(render_informe(idea, result), encoding="utf-8")

    icon = {"viable": "✅", "condicional": "⚠️", "descartar": "❌"}.get(result["veredicto"], "·")
    print(f"\n{icon} {result['titulo']}")
    print(f"   Veredicto: {result['veredicto']} ({result['score']}/100)")
    print(f"   Margen: {result['margen']['min']}-{result['margen']['max']}%")
    print(f"   → evaluaciones/{slug}/")
    print(f"      veredicto.json · informe.md\n")


def cmd_listar(_: argparse.Namespace) -> None:
    ev = ROOT / "evaluaciones"
    if not ev.exists():
        print("Sin evaluaciones aún.")
        return
    print("\nEvaluaciones:\n")
    for d in sorted(ev.iterdir()):
        if not d.is_dir():
            continue
        v = load_json(d / "veredicto.json", {})
        if v:
            print(f"  • {d.name}: {v.get('veredicto')} ({v.get('score')}/100)")


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluador de proyectos")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("evaluar", help="Evaluar una idea")
    e.add_argument("idea_file", nargs="?", help="ideas/archivo.json o .txt")
    e.add_argument("--texto", "-t", help="Idea en texto libre")
    e.add_argument("--slug", help="Slug de salida")
    e.set_defaults(func=cmd_evaluar)

    l = sub.add_parser("listar", help="Listar evaluaciones")
    l.set_defaults(func=cmd_listar)

    # Atajo: python evaluar.py ideas/foo.json
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in (
        "evaluar",
        "listar",
    ):
        sys.argv.insert(1, "evaluar")

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

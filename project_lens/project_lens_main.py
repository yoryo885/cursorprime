#!/usr/bin/env python3
"""CLI — Project Lens (evaluador de ideas, 13 agentes)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.compare import compare  # noqa: E402
from src.config import DEFAULT_SLUG, MOCK_WEB, load_json, save_json, slug_dir, slugify  # noqa: E402
from src.improvements import aplicar_mejoras  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def load_idea(path: Path | None, slug: str) -> tuple[dict, str]:
    if path:
        data = load_json(path, {}) or {}
        return data, slug or slugify(str(data.get("titulo") or path.stem))
    default = slug_dir(slug) / "inputs" / "idea.json"
    if default.exists():
        return load_json(default, {}) or {}, slug
    shared = ROOT.parent / "ideas de proyectos" / "ideas" / f"{slug}.json"
    if shared.exists():
        return load_json(shared, {}) or {}, slug
    raise SystemExit(f"No idea en data/{slug}/inputs/idea.json ni ideas/{slug}.json")


def cmd_analyze(args: argparse.Namespace) -> None:
    idea_path = Path(args.idea) if args.idea else None
    slug = args.slug or DEFAULT_SLUG
    idea, slug = load_idea(idea_path, slug)

    dest = slug_dir(slug) / "inputs" / "idea.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    save_json(dest, idea)

    if args.tipo:
        idea = {**idea, "tipo_negocio": args.tipo}

    modo = args.modo or "full"
    mock = MOCK_WEB if args.mock_web is None else args.mock_web

    print(f"\n🔍 Project Lens — {slug}")
    print(f"   Modo: {modo} · mock_web: {mock}\n")

    ok = run_pipeline(slug, idea, modo=modo, mock_web=mock, solo=args.solo)
    if ok:
        print(f"\n✅ Listo: data/{slug}/output/resumen.md\n")
    else:
        print("\n❌ Falló — logs/errores.json\n")
        sys.exit(1)


def cmd_batch(args: argparse.Namespace) -> None:
    folder = Path(args.batch)
    results = []
    for f in sorted(folder.glob("*.json")):
        slug = f.stem
        idea = load_json(f, {})
        print(f"\n--- {slug} ---")
        if run_pipeline(slug, idea, modo=args.modo or "mvp"):
            v = load_json(slug_dir(slug) / "meta" / "verdict.json", {})
            results.append({"slug": slug, "veredicto": v.get("veredicto"), "score": v.get("score_global", {}).get("point")})
    out = ROOT / "data" / "batch_summary.json"
    save_json(out, {"results": results, "count": len(results)})
    print(f"\n✅ Batch: {out}\n")


def cmd_compare(args: argparse.Namespace) -> None:
    r = compare(args.slug_a, args.slug_b)
    print(f"\nCompare: {r['ganador_global']} gana ({r['score_a']} vs {r['score_b']})\n")


def cmd_mejorar(args: argparse.Namespace) -> None:
    ok = run_pipeline(args.slug, load_idea(None, args.slug)[0], solo="improvement")
    if args.aplicar_mejoras:
        from src.config import slug_meta
        applied = aplicar_mejoras(slug_meta(args.slug), confirm=True)
        print("Aplicado:", applied)
    sys.exit(0 if ok else 1)


def main() -> None:
    p = argparse.ArgumentParser(description="Project Lens — evaluador de ideas")
    p.add_argument("--slug", default=DEFAULT_SLUG)
    p.add_argument("--idea", help="Ruta idea.json")
    p.add_argument("--modo", choices=["mvp", "full"], default="full")
    p.add_argument("--tipo", choices=["saas", "ecommerce", "marketplace", "servicio"])
    p.add_argument("--solo", help="Ejecutar un solo agente")
    p.add_argument("--mock-web", action="store_true", default=None)
    p.add_argument("--no-mock-web", action="store_true")
    p.add_argument("--batch", metavar="DIR", help="Analizar todos los .json")
    p.add_argument("--compare", nargs=2, metavar=("SLUG_A", "SLUG_B"))
    p.add_argument("--feedback", choices=["exito", "fracaso", "parcial", "sin_datos"])
    p.add_argument("--mejorar", action="store_true")
    p.add_argument("--aplicar-mejoras", action="store_true")
    args = p.parse_args()

    if args.no_mock_web:
        args.mock_web = False

    if args.compare:
        args.slug_a, args.slug_b = args.compare
        cmd_compare(args)
        return
    if args.batch:
        cmd_batch(args)
        return
    if args.mejorar:
        cmd_mejorar(args)
        return

    if args.feedback:
        from src.config import slug_meta
        fb_path = slug_meta(args.slug) / "feedback.json"
        save_json(fb_path, {"resultado_real": args.feedback})

    cmd_analyze(args)


if __name__ == "__main__":
    main()

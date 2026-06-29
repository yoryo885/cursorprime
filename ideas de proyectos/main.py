#!/usr/bin/env python3
"""
main.py — Meta-creador de proyectos pipeline.

Fase DISEÑO (siempre):
  python main.py diseñar ideas/ejemplo-idea.json
  python main.py diseñar --texto "Mi idea..."

Fase CONSTRUCCIÓN (solo cuando tú decidas):
  python main.py construir dropship_ml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import BORRADORES_DIR, IDEAS_DIR, load_json, slugify  # noqa: E402
from src.pipeline import CreatorPipeline  # noqa: E402


def load_idea(path: Path) -> dict:
    if path.suffix == ".json":
        return load_json(path, {}) or {}
    return {"titulo": path.stem, "problema": path.read_text(encoding="utf-8")}


def cmd_disenar(args: argparse.Namespace) -> None:
    if args.texto:
        idea = {"titulo": args.texto[:60], "problema": args.texto}
        slug = args.slug or slugify(args.texto[:40])
    elif args.idea_file:
        idea = load_idea(Path(args.idea_file))
        slug = (
            args.slug
            or str(idea.get("slug") or "").strip()
            or slugify(str(idea.get("titulo") or Path(args.idea_file).stem))
        )
    else:
        print("Indica ideas/archivo.json o --texto")
        sys.exit(1)

    print(f"\n📐 Fase DISEÑO — {slug}")
    print("   (No se creará nada en proyectos/)\n")
    CreatorPipeline(autorizado_construir=False).run_diseno(slug, idea)


def cmd_construir(args: argparse.Namespace) -> None:
    slug = args.slug
    print(f"\n🔨 Fase CONSTRUCCIÓN — {slug}\n")
    CreatorPipeline(autorizado_construir=True).run_construccion(slug)


def cmd_listar(_: argparse.Namespace) -> None:
    print("\n📋 Borradores:\n")
    if not BORRADORES_DIR.exists():
        print("  (ninguno)")
        return
    for d in sorted(BORRADORES_DIR.iterdir()):
        if not d.is_dir():
            continue
        feas = load_json(d / "meta" / "feasibility.json", {})
        veredicto = feas.get("veredicto", "?")
        print(f"  • {d.name} — {veredicto}")
        print(f"    borradores/{d.name}/DISEÑO.md")
    print("\n💡 Construir: python main.py construir <slug>")


def main() -> None:
    parser = argparse.ArgumentParser(description="Meta-creador de proyectos pipeline")
    sub = parser.add_subparsers(dest="cmd")

    p_dis = sub.add_parser("diseñar", help="Fase diseño → borradores/")
    p_dis.add_argument("idea_file", nargs="?", help="ideas/mi-idea.json")
    p_dis.add_argument("--texto", "-t", help="Idea en texto libre")
    p_dis.add_argument("--slug", help="Slug fijo")
    p_dis.set_defaults(func=cmd_disenar)

    p_build = sub.add_parser("construir", help="Fase construcción → proyectos/ (autorizado)")
    p_build.add_argument("slug", help="Slug del borrador")
    p_build.set_defaults(func=cmd_construir)

    p_list = sub.add_parser("listar", help="Listar borradores")
    p_list.set_defaults(func=cmd_listar)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()

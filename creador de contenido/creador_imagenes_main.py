#!/usr/bin/env python3
"""CLI — Creador de Contenido (imagen · gif · video · pdf · recetas de video)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_SLUG, load_json, slugify  # noqa: E402
from src.pipeline import AGENTS, run_pipeline  # noqa: E402
from src.recipes import load_recetas  # noqa: E402


def load_lote(path: Path | None, slug: str) -> tuple[dict, str]:
    if path:
        data = load_json(path, {}) or {}
        return data, slug or slugify(str(data.get("titulo") or path.stem))
    default = ROOT / "data" / slug / "inputs" / "lote.json"
    if default.exists():
        return load_json(default, {}) or {}, slug or DEFAULT_SLUG
    raise SystemExit(f"No hay lote en data/{slug}/inputs/lote.json")


def main() -> None:
    recetas = sorted(load_recetas().keys())
    p = argparse.ArgumentParser(
        description="Creador de Contenido — PNG/GIF/Video/PDF + recetas de video con agentes/skills"
    )
    p.add_argument("--slug", default=DEFAULT_SLUG)
    p.add_argument("--lote", help="Ruta a lote.json")
    p.add_argument(
        "--modo",
        choices=["all", "png", "gif", "video", "pdf"],
        default="all",
        help="Acota salidas medias (png|gif|video|pdf). Con receta, preferir --receta.",
    )
    p.add_argument(
        "--receta",
        choices=recetas or ["slideshow", "animado", "promo-guia", "reels-pack", "custom"],
        default=None,
        help="Receta de video: activa agentes/skills según necesidad (promo-guia, animado, …)",
    )
    p.add_argument(
        "--solo",
        choices=sorted(AGENTS.keys()),
        default=None,
        help="Ejecutar un solo agente (debug)",
    )
    p.add_argument(
        "--desde",
        choices=sorted(AGENTS.keys()),
        default=None,
        help="Reanudar el plan desde este agente (no rehace los anteriores)",
    )
    p.add_argument("--listar-recetas", action="store_true", help="Muestra recetas y sale")
    p.add_argument("--reset-checkpoint", action="store_true")
    args = p.parse_args()

    if args.listar_recetas:
        catalog = load_recetas()
        print("\nRecetas disponibles:\n")
        for rid, meta in catalog.items():
            skills = ", ".join(meta.get("skills") or []) or "—"
            print(f"  · {rid}: {meta.get('nombre')}")
            print(f"      skills: {skills}")
            print(f"      agentes: {', '.join(meta.get('agentes') or ['(custom)'])}")
            print()
        return

    lote_path = Path(args.lote) if args.lote else None
    lote, slug = load_lote(lote_path, args.slug)

    if args.receta:
        lote = {**lote, "receta": args.receta}

    dest = ROOT / "data" / slug / "inputs" / "lote.json"
    if lote_path or not dest.exists() or args.receta:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(lote, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.modo != "all" and not args.receta:
        lote = {**lote, "salidas": [args.modo]}

    print(f"\n📦 Creador de Contenido — {slug}")
    print(f"   Modo: {args.modo} · Receta: {args.receta or lote.get('receta') or '(auto)'}\n")

    ok = run_pipeline(
        slug=slug,
        lote=lote,
        modo=args.modo,
        reset=args.reset_checkpoint,
        receta=args.receta,
        solo=args.solo,
        desde=args.desde,
    )
    if ok:
        print(f"\n✅ Listo: data/{slug}/")
        print("   imagenes/ · videos/ · copy/ · meta/plan_runtime.json · output/\n")
    else:
        print("\n❌ Falló — logs/errores.json\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

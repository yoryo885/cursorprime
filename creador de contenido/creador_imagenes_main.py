#!/usr/bin/env python3
"""CLI — Creador de Contenido (imagen · gif · video · pdf)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_SLUG, load_json, slugify  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def load_lote(path: Path | None, slug: str) -> tuple[dict, str]:
    if path:
        data = load_json(path, {}) or {}
        return data, slug or slugify(str(data.get("titulo") or path.stem))
    default = ROOT / "data" / slug / "inputs" / "lote.json"
    if default.exists():
        return load_json(default, {}) or {}, slug or DEFAULT_SLUG
    raise SystemExit(f"No hay lote en data/{slug}/inputs/lote.json")


def main() -> None:
    p = argparse.ArgumentParser(description="Creador de Contenido")
    p.add_argument("--slug", default=DEFAULT_SLUG)
    p.add_argument("--lote", help="Ruta a lote.json")
    p.add_argument(
        "--modo",
        choices=["all", "png", "gif", "video", "pdf"],
        default="all",
        help="Salida: png | gif | video | pdf | all (usa salidas del lote.json)",
    )
    p.add_argument("--reset-checkpoint", action="store_true")
    args = p.parse_args()

    lote_path = Path(args.lote) if args.lote else None
    lote, slug = load_lote(lote_path, args.slug)

    dest = ROOT / "data" / slug / "inputs" / "lote.json"
    if lote_path or not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(lote, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.modo != "all":
        lote = {**lote, "salidas": [args.modo]}

    print(f"\n📦 Creador de Contenido — {slug}")
    print(f"   Modo: {args.modo}\n")

    ok = run_pipeline(slug=slug, lote=lote, modo=args.modo, reset=args.reset_checkpoint)
    if ok:
        print(f"\n✅ Listo: data/{slug}/")
        print("   imagenes/ · gifs/ · videos/ · pdf/ · output/\n")
    else:
        print("\n❌ Falló — logs/errores.json\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

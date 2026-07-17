#!/usr/bin/env python3
"""CLI — Pipeline Sitio PDF (tienda profesional para guías digitales)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import load_json, slug_output  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(
        description="Genera sitio PDF profesional: marca → imágenes IA → copy → Shopify + preview"
    )
    p.add_argument("cmd", choices=["generar", "status"], help="generar | status")
    p.add_argument("--slug", default="vertice-pro", help="Marca / carpeta data/{slug}/")
    p.add_argument("--producto", default="pareto", help="Slug producto en libros a entender")
    p.add_argument("--mock", action="store_true", default=True, help="Sin API imagen (default)")
    p.add_argument("--openai", action="store_true", help="Usar OpenAI para imágenes (pendiente)")
    p.add_argument("--reset-checkpoint", action="store_true")
    for paso in ("context", "visual", "copy", "qc", "assemble"):
        p.add_argument(f"--solo-{paso}", action="store_true")
    args = p.parse_args()

    if args.cmd == "status":
        meta = ROOT / "data" / args.slug / "meta"
        qc = load_json(meta / "qc_report.json", {})
        print("Pipeline sitio-pdf v0.1 — Vértice Pro")
        print(f"  QC ok: {qc.get('ok', '—')}")
        out = slug_output(args.slug)
        if (out / "preview.html").exists():
            print(f"  Preview: {out / 'preview.html'}")
        if (out / "vertice-pro-theme.zip").exists():
            print(f"  Zip: {out / 'vertice-pro-theme.zip'}")
        return

    solo = next((s for s in ("context", "visual", "copy", "qc", "assemble") if getattr(args, f"solo_{s}")), None)
    mock = not args.openai

    print(f"\nSitio PDF — {args.slug} / producto {args.producto} · modo {'mock' if mock else 'openai'}\n")

    ok = run_pipeline(
        slug=args.slug,
        producto=args.producto,
        mock=mock,
        reset=args.reset_checkpoint,
        solo=solo,
    )
    if ok:
        out = slug_output(args.slug)
        print(f"\n✅ Listo:")
        print(f"   → {out / 'preview.html'}")
        print(f"   → {out / 'vertice-pro-theme.zip'}")
        print(f"   → {out / 'assets/'}\n")
        sys.exit(0)
    print("\n❌ Falló — logs/errores.json\n")
    sys.exit(1)


if __name__ == "__main__":
    main()

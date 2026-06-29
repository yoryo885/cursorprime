#!/usr/bin/env python3
"""CLI — Centro de control prime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import CURSORPRIME, META_DIR, OUTPUT_DIR, save_json
from src.render_canvas import render_canvas
from src.render_html import render_html
from src.scanner import scan


def cmd_viabilidad(args) -> int:
    from src.viabilidad_web import investigar_todos, viabilidad_por_capas

    print("\n🔍 Viabilidad — YouTube + web (live)\n")
    items = investigar_todos(
        live=not args.mock,
        capa=args.capa or None,
        limit=args.limit,
        force=args.force,
    )
    res = viabilidad_por_capas(items)
    print(f"\n✅ {len(items)} proyectos · viables creador: {res['creador']['viables']} · productos: {res['productos']['viables']}")
    print("   → meta/viabilidad/*.json · refresh panel\n")
    if args.refresh:
        return cmd_refresh(args)
    return 0


def cmd_refresh(_args) -> int:
    inv = scan()
    save_json(META_DIR / "inventario.json", inv)
    html = render_html(inv, href_prefix="../../")
    canvas = render_canvas(inv)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "panel.html").write_text(render_html(inv, href_prefix="../../"), encoding="utf-8")
    (OUTPUT_DIR / "dashboard.canvas.tsx").write_text(canvas, encoding="utf-8")
    panel_copy = CURSORPRIME / "analisis-de-proyectos" / "PANEL-CONTROL.html"
    panel_copy.write_text(render_html(inv, href_prefix=""), encoding="utf-8")
    r = inv["resumen"]
    print("Centro de control prime — inventario actualizado")
    print(f"  Análisis: {r['analisis']} | Implementadas: {r['cola_implementadas']} | En espera: {r['cola_en_espera']}")
    print(f"  → meta/inventario.json")
    print(f"  → output/panel.html")
    print(f"  → output/dashboard.canvas.tsx")
    print(f"  → analisis-de-proyectos/PANEL-CONTROL.html")
    return 0


def cmd_resumen(_args) -> int:
    from src.config import load_json

    inv = load_json(META_DIR / "inventario.json")
    if not inv:
        print("Sin inventario. Ejecuta: python3 panel_main.py refresh")
        return 1
    r = inv.get("resumen", {})
    for k, v in r.items():
        print(f"  {k}: {v}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Centro de control prime — panel de inventario cursorprime")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("refresh", help="Escanear ecosistema y regenerar panel").set_defaults(func=cmd_refresh)
    v = sub.add_parser("viabilidad", help="Investigar viabilidad YouTube+web por proyecto")
    v.add_argument("--live", action="store_true", default=True, help="Fetch real (default)")
    v.add_argument("--mock", action="store_true", help="Sin red")
    v.add_argument("--capa", choices=["creador", "producto"], help="Solo una capa")
    v.add_argument("--limit", type=int, help="Máximo de proyectos")
    v.add_argument("--force", action="store_true", help="Repetir aunque haya cache")
    v.add_argument("--refresh", action="store_true", help="Regenerar panel al terminar")
    v.set_defaults(func=cmd_viabilidad)
    sub.add_parser("resumen", help="Mostrar resumen del último inventario").set_defaults(func=cmd_resumen)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

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


def cmd_serve(args) -> int:
    import re
    import shutil
    import subprocess
    import time
    from urllib.parse import quote

    if args.refresh:
        cmd_refresh(args)

    port = args.port
    root = CURSORPRIME
    panel_path = quote("centro de control prime/output/panel.html", safe="/")
    local = f"http://127.0.0.1:{port}/{panel_path}"

    # HTTP server
    if subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", local], capture_output=True, text=True).stdout.strip() != "200":
        subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--bind", "0.0.0.0"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for _ in range(20):
            if subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", local], capture_output=True, text=True).stdout.strip() == "200":
                break
            time.sleep(0.25)

    cloudflared = shutil.which("cloudflared") or "/tmp/cloudflared"
    if not Path(cloudflared).exists():
        print("cloudflared no encontrado. Instálalo o usa el enlace local en la misma red.")
        print(f"  Local: {local}")
        return 1

    log = OUTPUT_DIR / "cloudflared.log"
    url_file = OUTPUT_DIR / "panel-public-url.txt"
    subprocess.Popen(
        [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"],
        stdout=open(log, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    public = ""
    for _ in range(40):
        time.sleep(0.5)
        if log.exists():
            text = log.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", text)
            if m:
                public = m.group(0)
                break

    if not public:
        print("Servidor local activo, pero el túnel público tardó demasiado.")
        print(f"  Local: {local}")
        print(f"  Log: {log}")
        return 1

    public_panel = f"{public}/{panel_path}"
    url_file.write_text(public_panel + "\n", encoding="utf-8")
    print("Centro de control — enlace público listo")
    print(f"  Android / iPad: {public_panel}")
    print(f"  Local: {local}")
    print(f"  Guardado en: {url_file}")
    print("  Nota: el enlace trycloudflare.com es temporal mientras corra este proceso.")
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
    s = sub.add_parser("serve", help="Servir panel local + enlace público (Android/iPad)")
    s.add_argument("--port", type=int, default=8765, help="Puerto HTTP local (default 8765)")
    s.add_argument("--refresh", action="store_true", help="Regenerar panel antes de servir")
    s.set_defaults(func=cmd_serve)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

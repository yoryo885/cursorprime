#!/usr/bin/env python3
"""CLI — Marketing Audit (5 agentes paralelos → MARKETING-AUDIT.md)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.bridge_clientes import bridge_a_cliente  # noqa: E402
from src.config import DATA_DIR, DEFAULT_SLUG, load_json, slugify  # noqa: E402
from src.pipeline import run_audit  # noqa: E402


def load_brief(path: Path | None, url: str | None) -> dict:
    if path:
        return load_json(path, {}) or {}
    if url:
        return {"url": url}
    default = DATA_DIR / DEFAULT_SLUG / "inputs" / "brief.json"
    if default.exists():
        return load_json(default, {}) or {}
    raise SystemExit("Indica --url o --brief brief.json")


def cmd_audit(args: argparse.Namespace) -> None:
    brief = load_brief(Path(args.brief) if args.brief else None, args.url)
    slug = args.slug or slugify(str(brief.get("url") or "audit"))
    if args.cliente:
        brief["cliente"] = args.cliente
    if args.proyecto:
        brief["proyecto"] = args.proyecto

    ok = run_audit(slug=slug, brief=brief, reset=args.reset_checkpoint, pdf=args.pdf)
    if ok and args.cliente and args.proyecto:
        r = bridge_a_cliente(slug, args.cliente, args.proyecto)
        if r["ok"]:
            print(f"   📁 Cliente: {r['dest']}")
        else:
            print(f"   ⚠ Bridge: {r.get('error')}")
    sys.exit(0 if ok else 1)


def cmd_bridge(args: argparse.Namespace) -> None:
    r = bridge_a_cliente(args.slug, args.cliente, args.proyecto)
    if r["ok"]:
        print(f"✅ Copiado a {r['dest']}")
    else:
        print(f"❌ {r.get('error')}")
        sys.exit(1)


def cmd_listar(_: argparse.Namespace) -> None:
    if not DATA_DIR.exists():
        print("Sin audits en data/")
        return
    items = sorted(p for p in DATA_DIR.iterdir() if p.is_dir())
    print(f"\nAudits ({len(items)}):\n")
    for d in items:
        manifest = load_json(d / "output" / "manifest.json", {})
        score = manifest.get("score", "—")
        print(f"  • {d.name} — score {score}")


def main() -> None:
    p = argparse.ArgumentParser(description="Marketing Audit — 5 agentes en paralelo")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Auditar URL")
    a.add_argument("--url", "-u", help="URL del sitio")
    a.add_argument("--slug", "-s")
    a.add_argument("--brief", "-b")
    a.add_argument("--pdf", action="store_true", help="Generar MARKETING-REPORT.pdf")
    a.add_argument("--cliente", help="Slug cliente en clientes/")
    a.add_argument("--proyecto", help="Slug proyecto en clientes/{c}/proyectos/")
    a.add_argument("--reset-checkpoint", action="store_true")
    a.set_defaults(func=cmd_audit)

    b = sub.add_parser("bridge", help="Copiar output → clientes/")
    b.add_argument("slug")
    b.add_argument("--cliente", required=True)
    b.add_argument("--proyecto", required=True)
    b.set_defaults(func=cmd_bridge)

    l = sub.add_parser("listar", help="Listar audits en data/")
    l.set_defaults(func=cmd_listar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

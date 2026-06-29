#!/usr/bin/env python3
"""CLI — Análisis de proyectos (YouTube + web → idea de proyecto)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.bridge_proyectos import exportar_a_proyectos, listar_analisis  # noqa: E402
from src.config import DEFAULT_SLUG, META_DIR, MOCK_FETCH, load_json, slugify  # noqa: E402
from src.encadenar import encadenar  # noqa: E402
from src.pipeline import run_analisis  # noqa: E402
from src.radar import run_radar  # noqa: E402
from src.radar_scheduler import run_radar_auto  # noqa: E402


def load_brief(path: Path | None, texto: str | None, tema: str | None) -> dict:
    if path:
        return load_json(path, {}) or {}
    if texto or tema:
        t = tema or texto or ""
        return {
            "tema": t,
            "titulo": t[:80],
            "queries": [f"{t} youtube", f"{t} amazon kdp", f"{t} tendencias"],
        }
    default = ROOT / "data" / DEFAULT_SLUG / "inputs" / "brief.json"
    if default.exists():
        return load_json(default, {}) or {}
    raise SystemExit("Indica --texto, --tema o --brief brief.json")


def cmd_analizar(args: argparse.Namespace) -> None:
    if args.live:
        os.environ["MOCK_FETCH"] = "false"
    brief = load_brief(
        Path(args.brief) if args.brief else None,
        args.texto,
        args.tema,
    )
    slug = args.slug or slugify(str(brief.get("tema") or "analisis"))
    ok = run_analisis(slug=slug, brief=brief, reset=args.reset_checkpoint)
    if ok and args.exportar:
        r = exportar_a_proyectos(slug)
        if r["ok"]:
            print(f"   📤 Idea exportada: {r['path']}")
            if args.encadenar:
                chain = encadenar(slug, exportar=False, reset=args.reset_checkpoint)
                if not chain.get("ok"):
                    sys.exit(1)
    elif ok and args.encadenar:
        chain = encadenar(slug, exportar=True, reset=args.reset_checkpoint)
        if not chain.get("ok"):
            sys.exit(1)
    sys.exit(0 if ok else 1)


def cmd_radar(args: argparse.Namespace) -> None:
    if args.live:
        os.environ["MOCK_FETCH"] = "false"
    ok = run_radar(semana=args.semana, reset=args.reset_checkpoint)
    sys.exit(0 if ok else 1)


def cmd_radar_auto(args: argparse.Namespace) -> None:
    os.environ["MOCK_FETCH"] = "false"
    cfg = load_json(META_DIR / "radar_kdp.json", {}) or {}
    do_encadenar = args.encadenar or bool(cfg.get("auto_encadenar", False))
    r = run_radar_auto(
        semana=args.semana,
        force=args.force,
        exportar=args.exportar,
        encadenar=do_encadenar,
        reset=args.reset_checkpoint,
    )
    if r.get("skipped"):
        print(f"⏭ {r['mensaje']}")
        sys.exit(0)
    if r.get("exportado"):
        print(f"   📤 Exportado: {r['exportado']}")
    sys.exit(0 if r.get("ok") else 1)


def cmd_fetch_test(args: argparse.Namespace) -> None:
    os.environ["MOCK_FETCH"] = "false"
    from src.agents.fetch_agent import fetch_live

    t = args.texto or "kdp resumenes libros"
    queries = [t, f"{t} site:youtube.com"]
    yt, web, warnings = fetch_live(queries)
    print(f"\nFetch live — {len(yt)} YouTube · {len(web)} web\n")
    for item in yt[:5]:
        print(f"  [YT] {item.get('titulo', '')[:70]}")
        print(f"       {item.get('url')}\n")
    for item in web[:5]:
        print(f"  [WEB] {item.get('titulo', '')[:70]}")
        print(f"        {item.get('url')}\n")
    for w in warnings:
        print(f"  ⚠ {w}")
    sys.exit(0 if (yt or web) else 1)


def cmd_exportar(args: argparse.Namespace) -> None:
    r = exportar_a_proyectos(args.slug)
    if r["ok"]:
        print(f"✅ Exportado: {r['path']}")
        if args.encadenar:
            chain = encadenar(args.slug, exportar=False, reset=args.reset_checkpoint)
            sys.exit(0 if chain.get("ok") else 1)
        print(f"   Evaluar: cd ../ideas\\ de\\ proyectos && python3 evaluar.py ideas/from-analisis/{r['slug']}.json")
    else:
        print(f"❌ {r.get('error')}")
        sys.exit(1)


def cmd_encadenar(args: argparse.Namespace) -> None:
    chain = encadenar(
        args.slug,
        exportar=args.exportar,
        lluvia=not args.sin_lluvia,
        evaluar=not args.sin_evaluar,
        reset=args.reset_checkpoint,
    )
    if not chain.get("ok"):
        print(f"❌ {chain.get('error', 'Encadenar falló')}")
        sys.exit(1)
    print("\n✅ Encadenamiento completo\n")
    sys.exit(0)


def cmd_instalar_radar(_: argparse.Namespace) -> None:
    import shutil

    src = ROOT / "scripts" / "com.cursorprime.radar-kdp.plist"
    dest = Path.home() / "Library" / "LaunchAgents" / "com.cursorprime.radar-kdp.plist"
    if not src.exists():
        print(f"❌ No existe {src}")
        sys.exit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"✅ Copiado → {dest}")
    print("   Cargar: launchctl load ~/Library/LaunchAgents/com.cursorprime.radar-kdp.plist")
    print("   Radar: lunes 8:00 · log: logs/radar_cron.log")


def cmd_listar(_: argparse.Namespace) -> None:
    items = listar_analisis()
    print(f"\nAnálisis disponibles ({len(items)}):\n")
    for it in items:
        fetch_path = ROOT / "data" / it["slug"] / "meta" / "fetch.json"
        mode = "?"
        if fetch_path.exists():
            mode = "live" if not load_json(fetch_path, {}).get("mock") else "mock"
        print(f"  • {it['slug']}: {it.get('tema')} [{mode}]")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Análisis de proyectos — investigar mercado y preparar creación de pipelines"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analizar", help="YouTube + web → análisis")
    a.add_argument("--slug")
    a.add_argument("--texto", "-t")
    a.add_argument("--tema")
    a.add_argument("--brief")
    a.add_argument("--exportar", action="store_true", help="Exportar a ideas/from-analisis/")
    a.add_argument("--encadenar", action="store_true", help="Tras exportar: lluvia + evaluar")
    a.add_argument("--live", action="store_true", help="Fetch real (MOCK_FETCH=false)")
    a.add_argument("--reset-checkpoint", action="store_true")
    a.set_defaults(func=cmd_analizar)

    r = sub.add_parser("radar", help="Radar KDP semanal")
    r.add_argument("--semana")
    r.add_argument("--live", action="store_true", help="Fetch real")
    r.add_argument("--reset-checkpoint", action="store_true")
    r.set_defaults(func=cmd_radar)

    ra = sub.add_parser("radar-auto", help="Radar semanal automático (salta si ya corrió)")
    ra.add_argument("--semana")
    ra.add_argument("--force", action="store_true", help="Forzar aunque ya exista esta semana")
    ra.add_argument("--exportar", action="store_true", help="Exportar a ideas/from-analisis/")
    ra.add_argument("--encadenar", action="store_true", help="Tras exportar: lluvia + evaluar (o radar_kdp auto_encadenar)")
    ra.add_argument("--reset-checkpoint", action="store_true")
    ra.set_defaults(func=cmd_radar_auto)

    f = sub.add_parser("fetch-test", help="Probar búsqueda live sin pipeline completo")
    f.add_argument("--texto", "-t", default="kdp resumenes libros")
    f.set_defaults(func=cmd_fetch_test)

    e = sub.add_parser("exportar", help="Análisis → borrador en ideas de proyectos")
    e.add_argument("slug")
    e.add_argument("--encadenar", action="store_true", help="Lluvia + evaluar tras exportar")
    e.add_argument("--reset-checkpoint", action="store_true")
    e.set_defaults(func=cmd_exportar)

    c = sub.add_parser("encadenar", help="Exportar (opcional) → lluvia → evaluar")
    c.add_argument("slug", help="Slug del análisis en data/")
    c.add_argument("--exportar", action="store_true", help="Re-exportar idea antes de encadenar")
    c.add_argument("--sin-lluvia", action="store_true")
    c.add_argument("--sin-evaluar", action="store_true")
    c.add_argument("--reset-checkpoint", action="store_true")
    c.set_defaults(func=cmd_encadenar)

    l = sub.add_parser("listar", help="Listar análisis en data/")
    l.set_defaults(func=cmd_listar)

    i = sub.add_parser("instalar-radar", help="Instalar radar semanal en launchd (macOS)")
    i.set_defaults(func=cmd_instalar_radar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

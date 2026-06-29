#!/usr/bin/env python3
"""CLI — Lluvia de ideas (propuestas con tu OK; análisis en analisis-de-proyectos)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

ANALISIS_ROOT = ROOT.parent / "analisis-de-proyectos"
ANALISIS_CLI = ANALISIS_ROOT / "analisis_main.py"
DEFAULT_ANALISIS_SLUG = "demo_investigacion"

from src.bridge_contenido import run_pack_visual  # noqa: E402
from src.bridge_ideas import exportar_aprobadas, marcar_implementada  # noqa: E402
from src.cola import aprobar, listar_cola, posponer, rechazar  # noqa: E402
from src.config import load_json, slugify  # noqa: E402
from src.pipeline_lluvia import run_lluvia  # noqa: E402


def _run_analisis_cli(*extra: str) -> int:
    if not ANALISIS_CLI.exists():
        print(f"❌ Falta analisis-de-proyectos: {ANALISIS_CLI}")
        return 1
    cmd = [sys.executable, str(ANALISIS_CLI), *extra]
    return subprocess.run(cmd, cwd=str(ANALISIS_ROOT)).returncode


def cmd_investigar(args: argparse.Namespace) -> None:
    extra = ["analizar"]
    if args.texto:
        extra += ["--texto", args.texto]
    if args.tema:
        extra += ["--tema", args.tema]
    if args.brief:
        extra += ["--brief", args.brief]
    if args.slug:
        extra += ["--slug", args.slug]
    if args.reset_checkpoint:
        extra.append("--reset-checkpoint")
    sys.exit(_run_analisis_cli(*extra))


def cmd_lluvia(args: argparse.Namespace) -> None:
    analisis_slug = args.desde_analisis or args.slug.replace("lluvia_", "", 1) or DEFAULT_ANALISIS_SLUG
    slug = args.slug or f"lluvia_{analisis_slug}"
    brief = {"analisis_slug": analisis_slug}
    if args.tema:
        brief["tema"] = args.tema
    ok = run_lluvia(
        slug=slug,
        brief=brief,
        analisis_slug=analisis_slug,
        reset=args.reset_checkpoint,
    )
    sys.exit(0 if ok else 1)


def cmd_todo(args: argparse.Namespace) -> None:
    extra = ["analizar"]
    if args.texto:
        extra += ["--texto", args.texto]
    if args.tema:
        extra += ["--tema", args.tema]
    if args.brief:
        extra += ["--brief", args.brief]
    if args.slug:
        extra += ["--slug", args.slug]
    if args.reset_checkpoint:
        extra.append("--reset-checkpoint")
    slug = args.slug or slugify(str(args.tema or args.texto or "investigacion"))
    if _run_analisis_cli(*extra) != 0:
        sys.exit(1)
    lluvia_slug = f"lluvia_{slug}"
    if not run_lluvia(slug=lluvia_slug, analisis_slug=slug, reset=args.reset_checkpoint):
        sys.exit(1)


def cmd_cola_listar(_: argparse.Namespace) -> None:
    data = listar_cola()
    for estado, items in data.items():
        print(f"\n## {estado.upper()} ({len(items)})\n")
        if not items:
            print("  (vacío)")
            continue
        for idea in items:
            print(f"  • [{idea.get('id')}] {idea.get('titulo')}")
            print(f"    {idea.get('categoria')} → {idea.get('proyecto_afectado')} (conf. {idea.get('confidence')})")


def cmd_radar(args: argparse.Namespace) -> None:
    extra = ["radar"]
    if args.semana:
        extra += ["--semana", args.semana]
    if args.reset_checkpoint:
        extra.append("--reset-checkpoint")
    sys.exit(_run_analisis_cli(*extra))


def cmd_pack_visual(args: argparse.Namespace) -> None:
    slug = args.desde_analisis or DEFAULT_ANALISIS_SLUG
    ok = run_pack_visual(analisis_slug=slug, pack_slug=args.slug)
    sys.exit(0 if ok else 1)


def cmd_puente_exportar(_: argparse.Namespace) -> None:
    results = exportar_aprobadas(evaluar_nuevo_proyecto=False)
    print(f"\n📤 Exportadas {len(results)} ideas → ideas de proyectos/ideas/from-lluvia/\n")
    for r in results:
        print(f"  • {r.get('slug')}: {r.get('path')}")


def cmd_implementar_aprobadas(args: argparse.Namespace) -> None:
    analisis = args.desde_analisis or DEFAULT_ANALISIS_SLUG
    ok = True

    print("\n═══ 1/3 Radar KDP semanal ═══")
    if _run_analisis_cli("radar", *(["--reset-checkpoint"] if args.reset_checkpoint else [])) != 0:
        ok = False

    print("\n═══ 2/3 Pack visual post-investigación ═══")
    if not run_pack_visual(analisis_slug=analisis):
        ok = False

    print("\n═══ 3/3 Puente → ideas de proyectos ═══")
    exportar_aprobadas()
    print("   Exportadas a ideas/from-lluvia/")

    for idea_id, nota in (
        ("idea-86066e0f", "radar semanal + meta/radar_kdp.json"),
        ("idea-4f897bfa", f"pack visual desde {analisis}"),
        ("idea-8201d58d", "export automático en cola aprobar + puente exportar"),
    ):
        marcar_implementada(idea_id, nota)
        print(f"   ✓ {idea_id} implementada")

    print("\n✅ Ideas aprobadas implementadas\n" if ok else "\n⚠️ Completado con errores\n")
    sys.exit(0 if ok else 1)


def cmd_cola_aprobar(args: argparse.Namespace) -> None:
    r = aprobar(args.idea_id, args.nota or "")
    if r["ok"]:
        print(f"✅ Aprobada: {args.idea_id}")
        print("   Exportada → ideas de proyectos/ideas/from-lluvia/")
    else:
        print(f"❌ {r.get('error')}")
        sys.exit(1)


def cmd_cola_posponer(args: argparse.Namespace) -> None:
    r = posponer(args.idea_id, args.nota or "")
    if r["ok"]:
        print(f"⏸ En espera: {args.idea_id} (revisar después)")
    else:
        print(f"❌ {r.get('error')}")
        sys.exit(1)


def cmd_cola_rechazar(args: argparse.Namespace) -> None:
    r = rechazar(args.idea_id, args.motivo or "")
    if r["ok"]:
        print(f"🗑 Rechazada: {args.idea_id}")
    else:
        print(f"❌ {r.get('error')}")
        sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description="Lluvia de ideas — investigación + cola con OK humano")
    sub = p.add_subparsers(dest="cmd", required=True)

    inv = sub.add_parser("investigar", help="→ analisis-de-proyectos analizar")
    inv.add_argument("--slug")
    inv.add_argument("--texto", "-t", help="Tema en texto libre")
    inv.add_argument("--tema", help="Tema corto")
    inv.add_argument("--brief", help="Ruta a brief.json")
    inv.add_argument("--reset-checkpoint", action="store_true")
    inv.set_defaults(func=cmd_investigar)

    llu = sub.add_parser("lluvia", help="Análisis + dirección → ideas pendientes")
    llu.add_argument("--slug", default="")
    llu.add_argument("--desde-analisis", help="Slug del análisis previo")
    llu.add_argument("--tema")
    llu.add_argument("--reset-checkpoint", action="store_true")
    llu.set_defaults(func=cmd_lluvia)

    todo = sub.add_parser("todo", help="investigar + lluvia en secuencia")
    todo.add_argument("--slug")
    todo.add_argument("--texto", "-t")
    todo.add_argument("--tema")
    todo.add_argument("--brief")
    todo.add_argument("--reset-checkpoint", action="store_true")
    todo.set_defaults(func=cmd_todo)

    rad = sub.add_parser("radar", help="→ analisis-de-proyectos radar")
    rad.add_argument("--semana", help="Ej: 2026w26 (default: semana actual)")
    rad.add_argument("--reset-checkpoint", action="store_true")
    rad.set_defaults(func=cmd_radar)

    pv = sub.add_parser("pack-visual", help="Análisis → 3 PNG + GIF en creador de contenido")
    pv.add_argument("--desde-analisis", default=DEFAULT_ANALISIS_SLUG)
    pv.add_argument("--slug", help="Slug del pack en creador de contenido")
    pv.set_defaults(func=cmd_pack_visual)

    pe = sub.add_parser("puente-exportar", help="Exportar aprobadas a ideas de proyectos")
    pe.set_defaults(func=cmd_puente_exportar)

    imp = sub.add_parser("implementar-aprobada", help="Ejecutar las 3 ideas aprobadas")
    imp.add_argument("--desde-analisis", default=DEFAULT_ANALISIS_SLUG)
    imp.add_argument("--reset-checkpoint", action="store_true")
    imp.set_defaults(func=cmd_implementar_aprobadas)

    cola = sub.add_parser("cola", help="Gestionar aprobaciones")
    cola_sub = cola.add_subparsers(dest="cola_cmd", required=True)

    cl = cola_sub.add_parser("listar")
    cl.set_defaults(func=cmd_cola_listar)

    ca = cola_sub.add_parser("aprobar")
    ca.add_argument("idea_id")
    ca.add_argument("--nota", default="")
    ca.set_defaults(func=cmd_cola_aprobar)

    cp = cola_sub.add_parser("posponer", help="Guardar en en_espera (no rechazar)")
    cp.add_argument("idea_id")
    cp.add_argument("--nota", default="")
    cp.set_defaults(func=cmd_cola_posponer)

    cr = cola_sub.add_parser("rechazar")
    cr.add_argument("idea_id")
    cr.add_argument("--motivo", default="")
    cr.set_defaults(func=cmd_cola_rechazar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

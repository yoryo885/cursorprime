#!/usr/bin/env python3
"""CLI — Pipeline de agentes para generar landings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from src.llm_client import LLMClient
from src.pipeline import run_pipeline

# Demo Vértice Pro (producto de prueba del ecosistema)
DEMO_VERTICE = {
    "slug": "vertice-pro",
    "marca": "Vértice Pro",
    "nombre_producto": "Vértice Pro",
    "producto": "Guías PDF libro × rol",
    "rubro": "educacion / productividad profesional",
    "precio": "desde $4.99",
    "publico": "psicopedagogas, docentes y profesionales por oficio",
    "tono": "editorial, claro, sin relleno",
    "propuesta_valor": "Métodos de libros clásicos, aplicados a tu oficio",
    "promesa": "Métodos de libros clásicos, aplicados a tu oficio",
    "cta": "Ver colección",
    "contacto": "hola@vertice.pro",
    "n_productos": 6,
    "n_roles": 5,
    "testimonios": [],
    "extras": {"redes": []},
}


def cmd_run(args: argparse.Namespace) -> None:
    if args.demo:
        negocio = dict(DEMO_VERTICE)
    else:
        if not args.input:
            print("❌ Usá --demo o --input brief.json")
            sys.exit(1)
        negocio = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.slug:
        negocio["slug"] = args.slug

    llm = LLMClient()
    mode = "mock" if llm.mock else f"claude:{llm.model}"
    print(f"\n🚀 Landing pipeline — {negocio.get('slug')} ({mode})\n")
    result = run_pipeline(
        negocio,
        llm=llm,
        solo=args.solo,
        retry_from=args.retry_from,
    )
    qa = result.get("qa") or {}
    visual = result.get("visual_qa") or {}
    print(f"\n✅ Listo → {result['out']}")
    print(f"   landing: {result['landing']}")
    print(f"   copy:    {Path(result['out']) / 'copy.json'}")
    print(f"   QA score: {qa.get('score', '—')}")
    if qa.get("bugs_v2"):
        print(f"   bugs_v2: {qa['bugs_v2']}")
    if qa.get("omisiones"):
        print(f"   omisiones: {qa['omisiones']}")
    if qa.get("criticos"):
        print(f"   críticos: {qa['criticos']}")
    if visual.get("skipped"):
        print(f"   visual_qa: skipped ({visual.get('motivo')})")
    elif visual:
        print(f"   screenshots: {visual.get('screenshots')}")
        print(f"   overlaps: {visual.get('overlaps')}")
    print()


def cmd_list_skills(_: argparse.Namespace) -> None:
    skills = sorted((ROOT / "src" / "skills").glob("*.md"))
    print("\nSkills:")
    for s in skills:
        print(f"  · {s.name}")
    print()


def main() -> None:
    p = argparse.ArgumentParser(description="Landing pipeline (agentes + skills)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Correr pipeline")
    r.add_argument("--demo", action="store_true", help="Demo Vértice Pro")
    r.add_argument("--input", default="", help="JSON de negocio")
    r.add_argument("--slug", default="")
    r.add_argument("--solo", default=None, help="Solo un agente (ej. 02_hero)")
    r.add_argument("--retry-from", default=None, help="Reanudar desde agente")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("skills", help="Listar skills")
    s.set_defaults(func=cmd_list_skills)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

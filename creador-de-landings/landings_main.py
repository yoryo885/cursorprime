#!/usr/bin/env python3
"""CLI — Creador de Landings (entrevista → ejemplos → HTML)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.catalog import ensure_catalog  # noqa: E402
from src.config import load_json, preguntas_path, save_json, slug_inputs, slug_output  # noqa: E402
from src.interview import DEMO_RESPUESTAS, run_interview  # noqa: E402
from src.learning import load_mejoras, registrar_mejora  # noqa: E402
from src.answers import resolver_respuestas  # noqa: E402
from src.palettes import formato_chat_paletas  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def cmd_responder(args: argparse.Namespace) -> None:
    """Guarda respuestas desde letras A/B/C/D y opcionalmente genera."""
    slug = args.slug
    resolved = resolver_respuestas(args.letras)
    dest = slug_inputs(slug)
    dest.mkdir(parents=True, exist_ok=True)
    save_json(dest / "respuestas.json", resolved)
    print(f"\n✅ Respuestas → {dest / 'respuestas.json'}")
    for k, v in resolved.items():
        if not k.startswith("_"):
            print(f"  · {k}: {v}")
    if args.generar:
        estilo = resolved.get("estilo") or resolved.get("ejemplo_elegido") or "tienda"
        ok = run_pipeline(slug=slug, respuestas=resolved, ejemplo=estilo, reset=True)
        if ok:
            print(f"\n✅ Landing: {slug_output(slug) / 'preview.html'}\n")
            sys.exit(0)
        sys.exit(1)
    print(f"\nSiguiente: python3 landings_main.py generar --slug {slug}\n")


def cmd_preguntas(_args: argparse.Namespace) -> None:
    """Imprime la entrevista estándar con opciones A/B/C/D."""
    spec = load_json(preguntas_path(), {}) or {}
    print(f"\n{spec.get('titulo', 'Entrevista estándar')}")
    print(spec.get("intro", ""))
    print()
    for i, q in enumerate(spec.get("preguntas") or [], 1):
        rec = (q.get("recomendado") or "A").upper()
        print(f"{i}. {q['texto']}")
        for let in ("A", "B", "C", "D"):
            opt = (q.get("opciones") or {}).get(let)
            if not opt:
                continue
            mark = " ★" if let == rec else ""
            print(f"   {let}) {opt}{mark if '★' not in opt else ''}")
        print()
    recs = (spec.get("recomendacion_default") or {}).get("letras_recomendadas", "")
    if recs:
        print(f"Recomendado: {recs}")
        print("Atajo: responde `todo A` (o pega la línea recomendada).")
    print()
    print(formato_chat_paletas({"clima_color": "neutro", "tono": "editorial", "estilo": "tienda"}))
    print()
    print("Fuente: meta/preguntas.json\n")


def cmd_entrevista(args: argparse.Namespace) -> None:
    slug = args.slug or "mi-landing"
    run_interview(slug, interactive=not args.no_interactive)
    print("Siguiente: revisa ejemplos con:")
    print(f"  python3 landings_main.py ejemplos --slug {slug}")
    print(f"  python3 landings_main.py generar --slug {slug} --ejemplo editorial")


def cmd_generar(args: argparse.Namespace) -> None:
    slug = args.slug
    resp_path = slug_inputs(slug) / "respuestas.json"
    if not resp_path.exists():
        print("❌ No hay respuestas. Usa entrevista o demo.")
        sys.exit(1)
    respuestas = load_json(resp_path, {}) or {}
    if args.ejemplo:
        respuestas["ejemplo_elegido"] = args.ejemplo
        save_json(resp_path, respuestas)
    print(f"\n🚀 Creador de Landings — {slug}\n")
    ok = run_pipeline(
        slug=slug,
        respuestas=respuestas,
        ejemplo=args.ejemplo or "",
        reset=args.reset_checkpoint,
        solo=args.solo,
    )
    if ok:
        out = slug_output(slug)
        print(f"\n✅ Listo:")
        print(f"   → {out / 'preview.html'}")
        print(f"   → {out / 'ejemplos.md'}")
        print(f"   → {out / 'brief.md'}\n")
        sys.exit(0)
    print("\n❌ Falló — logs/errores.json\n")
    sys.exit(1)


def cmd_aprender(args: argparse.Namespace) -> None:
    entry = registrar_mejora(args.mensaje, args.cambio or args.mensaje, aplicado=True)
    print(f"\n🧠 Mejora registrada: {entry['id']}")
    print(f"   {entry['cambio']}\n")
    print("Se aplicará en la próxima generación (brief + HTML).\n")
    data = load_mejoras()
    print(f"Total mejoras: {len(data.get('mejoras', []))}")


def cmd_demo(args: argparse.Namespace) -> None:
    slug = args.slug or "demo-cliente"
    print("\n👤 Demo cliente — Vértice Pro (catálogo multi-producto)\n")
    dest = slug_inputs(slug)
    dest.mkdir(parents=True, exist_ok=True)
    save_json(dest / "respuestas.json", DEMO_RESPUESTAS)
    cat = ensure_catalog(slug)
    print(f"  · catálogo: {len(cat.get('catalogo_guias', []))} guías · {len(cat.get('roles', []))} roles")
    for k, v in DEMO_RESPUESTAS.items():
        if not k.startswith("_"):
            print(f"  · {k}: {v}")
    print()
    print("📋 Generando ejemplos + landing con colección completa...\n")
    ok = run_pipeline(
        slug=slug,
        respuestas=dict(DEMO_RESPUESTAS),
        ejemplo=args.ejemplo or DEMO_RESPUESTAS.get("estilo") or "tienda",
        reset=True,
    )
    if not ok:
        print("\n❌ Demo falló\n")
        sys.exit(1)
    out = slug_output(slug)
    print(f"\n✅ Demo lista (cliente: Vértice Pro)")
    print(f"   Ejemplos: {out / 'ejemplos.md'}")
    print(f"   Brief:    {out / 'brief.md'}")
    print(f"   Landing:  {out / 'preview.html'}")
    print("\nAbre el HTML en el navegador para ver el resultado.\n")
    sys.exit(0)


def main() -> None:
    p = argparse.ArgumentParser(description="Creador de Landings — cursorprime")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("entrevista", help="Preguntas de brief")
    e.add_argument("--slug", default="mi-landing")
    e.add_argument("--no-interactive", action="store_true", help="Usar defaults sin pedir input")
    e.set_defaults(func=cmd_entrevista)

    g = sub.add_parser("generar", help="Generar landing desde respuestas")
    g.add_argument("--slug", required=True)
    g.add_argument("--ejemplo", choices=["editorial", "tienda", "mockup", "oferta"], default="")
    g.add_argument("--reset-checkpoint", action="store_true")
    g.add_argument("--solo", choices=["interview", "examples", "brief", "build", "qc", "packager"])
    g.set_defaults(func=cmd_generar)

    x = sub.add_parser("ejemplos", help="Solo proponer estilos")
    x.add_argument("--slug", required=True)
    x.add_argument("--reset-checkpoint", action="store_true")
    x.set_defaults(func=lambda a: _cmd_ejemplos_fixed(a))

    d = sub.add_parser("demo", help="Correr como cliente demo (Vértice Pro)")
    d.add_argument("--slug", default="demo-cliente")
    d.add_argument("--ejemplo", choices=["editorial", "tienda", "mockup", "oferta"], default="tienda")
    d.set_defaults(func=cmd_demo)

    q = sub.add_parser("preguntas", help="Mostrar entrevista estándar A/B/C/D")
    q.set_defaults(func=cmd_preguntas)

    r = sub.add_parser("responder", help="Guardar respuestas desde letras (1A 2B…)")
    r.add_argument("--slug", default="demo-cliente")
    r.add_argument("--letras", required=True, help="Ej: '1A 2A 3A…' o 'todo A'")
    r.add_argument("--generar", action="store_true")
    r.set_defaults(func=cmd_responder)

    a = sub.add_parser("aprender", help="Registrar mejora para próximas generaciones")
    a.add_argument("--mensaje", required=True, help="Qué dijo el usuario")
    a.add_argument("--cambio", default="", help="Cómo se aplica en el sistema")
    a.set_defaults(func=cmd_aprender)

    args = p.parse_args()
    args.func(args)


def _cmd_ejemplos_fixed(args: argparse.Namespace) -> None:
    slug = args.slug
    if not (slug_inputs(slug) / "respuestas.json").exists():
        print("❌ Falta entrevista.")
        sys.exit(1)
    print(f"\n🎨 Ejemplos — {slug}\n")
    # run only up to examples: interview (load) + examples
    ok = run_pipeline(slug=slug, reset=args.reset_checkpoint, solo="interview")
    ok = ok and run_pipeline(slug=slug, reset=False, solo="examples")
    if ok:
        print(f"\n✅ {slug_output(slug) / 'ejemplos.md'}\n")
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()

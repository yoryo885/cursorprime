#!/usr/bin/env python3
"""
plan.py — Agente planificador (independiente del pipeline de generación).

Ejemplos:
  python plan.py "Quiero un resumen de El principio de Pareto dedicado a soldadores"

  python plan.py "Resumen Pareto para psicopedagogas" --libro "El principio de Pareto" --slug pareto

  python plan.py --ejecutar --slug pareto --sin-confirmacion
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.agents.planner_agent import PlannerAgent, plan_path_for
from src.config import ANTHROPIC_API_KEY, RESUMENES_DIR
from src.plan_executor import PlanExecutor, resolve_book_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Planifica un resumen editorial a partir de tu pedido en lenguaje natural.",
    )
    parser.add_argument(
        "brief",
        nargs="?",
        default="",
        help='Ej: "Quiero un resumen de Pareto dedicado a soldadores"',
    )
    parser.add_argument("--libro", default="", help="Nombre o ruta del PDF/libro")
    parser.add_argument("--profesion", default="", help="Profesión u oficio del lector objetivo")
    parser.add_argument("--slug", default="", help="Carpeta de salida en resumenes/")
    parser.add_argument("--temas", nargs="*", help="Temas fijos (opcional)")
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Tras planificar, ejecuta el pipeline completo con el plan guardado",
    )
    parser.add_argument(
        "--solo-planificar",
        action="store_true",
        help="Solo genera y guarda el plan (por defecto si no pasas --ejecutar)",
    )
    parser.add_argument("--sin-confirmacion", action="store_true")
    parser.add_argument("--sin-imagenes", action="store_true")
    parser.add_argument("--max-subagentes", type=int, default=4)
    parser.add_argument(
        "--sin-qc",
        action="store_true",
        help="No ejecutar control de calidad final tras generar",
    )
    parser.add_argument(
        "--solo-qc",
        action="store_true",
        help="Solo revisar tablas + PDF del slug (sin generar)",
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Regenerar todo desde cero (ignora progreso existente)",
    )
    parser.add_argument(
        "--desde",
        choices=("auto", "resumenes", "tablas", "pdf"),
        default="auto",
        help="Paso inicial: auto continúa donde quedó; resumenes|tablas|pdf fuerzan el inicio",
    )
    return parser.parse_args()


def _ensure_llm():
    if not ANTHROPIC_API_KEY:
        raise ValueError("Se requiere ANTHROPIC_API_KEY en .env para planificar.")
    from src.llm import LLMClient

    return LLMClient(ANTHROPIC_API_KEY)


def _print_plan(plan) -> None:
    print("\n📋 Plan editorial")
    print(f"   Libro:      {plan.libro_nombre}")
    print(f"   Slug:       {plan.libro_slug}")
    print(f"   Audiencia:  {plan.audiencia}")
    print(f"   PDF:        {plan.pdf_path}")
    print(f"   Temas ({len(plan.temas)}):")
    for i, tema in enumerate(plan.temas, 1):
        print(f"      {i:02d}. {tema}")
    print("   Contexto lector:")
    for k, v in plan.contexto_usuario.items():
        if v:
            print(f"      · {k}: {v}")
    print("   Pasos:")
    for paso in plan.pasos:
        print(f"      · {paso}")
    if plan.notas:
        print(f"   Notas: {plan.notas}")


def _confirm_cost(
    plan,
    pdf_path: str,
    sin_confirmacion: bool,
    *,
    desde: str = "auto",
    forzar: bool = False,
) -> bool:
    from src.cost_estimator import estimar, mostrar_y_confirmar
    from src.pdf_reader import extract_text
    from src.plan_executor import PlanExecutor

    try:
        pdf_text = extract_text(pdf_path)
    except Exception:
        pdf_text = " " * 5000

    executor = PlanExecutor(plan, desde=desde, forzar=forzar)
    modo_coste = {
        "completo": "completo",
        "enriquecer": "enriquecer",
        "pdf": "pdf",
    }.get(executor._resolve_modo(executor.progress()), "completo")

    estimacion = estimar(pdf_text, plan.temas, modo=modo_coste)
    if sin_confirmacion:
        print(
            f"📊 Costo estimado ({estimacion['modo']}): ${estimacion['costo_usd']} USD — "
            f"~{estimacion['llamadas_estimadas']} llamadas LLM — "
            f"{estimacion['tiempo_estimado_min']} min"
        )
        return True
    return mostrar_y_confirmar(estimacion)


def _ejecutar_plan(plan, args) -> None:
    try:
        pdf = resolve_book_pdf(plan.pdf_path or plan.libro_nombre)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    if not _confirm_cost(
        plan,
        str(pdf),
        args.sin_confirmacion,
        desde=args.desde,
        forzar=args.forzar,
    ):
        print("Cancelado.")
        sys.exit(0)

    try:
        PlanExecutor(
            plan,
            max_subagentes=args.max_subagentes,
            sin_imagenes=args.sin_imagenes,
            sin_qc=args.sin_qc,
            forzar=args.forzar,
            desde=args.desde,
        ).execute()
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        sys.exit(1)


def main() -> None:
    args = parse_args()

    if args.solo_qc:
        if not args.slug:
            print("❌ --solo-qc requiere --slug")
            sys.exit(1)
        from src.agents.final_qc_agent import run_qc_for_slug
        sys.exit(run_qc_for_slug(args.slug))

    if args.ejecutar and not args.brief and not args.libro:
        output_dir = RESUMENES_DIR / (args.slug or "")
        if not args.slug:
            print("❌ Con --ejecutar solo, indica --slug")
            sys.exit(1)
        plan = PlannerAgent.load(output_dir)
        _print_plan(plan)
        _ejecutar_plan(plan, args)
        return

    if not args.brief and not args.libro:
        print('❌ Indica tu pedido. Ej: python plan.py "Resumen Pareto para soldadores"')
        sys.exit(1)

    llm = _ensure_llm()
    planner = PlannerAgent(llm)
    plan = planner.run(
        args.brief,
        libro=args.libro,
        slug=args.slug,
        profesion=args.profesion,
        temas=args.temas or None,
    )
    plan_path = planner.save(plan)
    _print_plan(plan)
    print(f"\n💾 Plan guardado: {plan_path}")
    print(f"💾 Contexto:      {plan_path.parent.parent / 'contexto_usuario.json'}")
    print(
        f"\n▶ Para ejecutar todo el pipeline:\n"
        f"   python plan.py --ejecutar --slug {plan.libro_slug} --sin-confirmacion"
    )
    print(
        f"   (auto continúa donde quedó; --forzar regenera todo; "
        f"--desde tablas|pdf para reanudar en un paso concreto)"
    )

    if args.ejecutar:
        _ejecutar_plan(plan, args)


if __name__ == "__main__":
    main()

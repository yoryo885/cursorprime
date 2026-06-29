#!/usr/bin/env python3
"""
main.py — punto de entrada del sistema.

Uso:
  python main.py "Pensar Rápido, Pensar Despacio" \\
      "Sistema 1 y Sistema 2" "Sesgos cognitivos" --slug kahneman

  python main.py "Pensar Rápido" --solo-enriquecer --slug kahneman
"""
import argparse
import sys
from pathlib import Path

from src.models import BookJob
from src.main_agent import MainAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera resúmenes en primera persona desde un PDF."
    )
    parser.add_argument("libro", nargs="?", default="", help="Nombre del libro (sin .pdf) o ruta al archivo")
    parser.add_argument("temas", nargs="*", help="Temas a resumir")
    parser.add_argument("--slug", default="", help="Identificador de carpeta de salida")
    parser.add_argument("--max-subagentes", type=int, default=4)
    parser.add_argument(
        "--solo-enriquecer",
        action="store_true",
        help="Leer .md existente y regenerar tablas/mapa/imágenes/PDF",
    )
    parser.add_argument(
        "--sin-llm",
        action="store_true",
        help="Solo imágenes + PDF, sin llamadas a Claude",
    )
    parser.add_argument(
        "--sin-confirmacion",
        action="store_true",
        help="No pedir confirmación de costo",
    )
    parser.add_argument(
        "--sin-imagenes",
        action="store_true",
        help="No descargar ni integrar imágenes Unsplash",
    )
    parser.add_argument(
        "--sin-md",
        action="store_true",
        help="No regenerar el archivo .md",
    )
    parser.add_argument(
        "--solo-mapa",
        action="store_true",
        help="Solo generar mapa conceptual (requiere .md existente)",
    )
    parser.add_argument(
        "--solo-tablas",
        action="store_true",
        help="Solo generar tablas con diseños variados (requiere .md existente)",
    )
    parser.add_argument(
        "--solo-pdf",
        action="store_true",
        help="Solo ensamblar PDF editorial HTML+Playwright (requiere .md existente)",
    )
    parser.add_argument(
        "--solo-intros",
        action="store_true",
        help="Solo generar intro general para quién es el resumen (requiere .md existente)",
    )
    parser.add_argument(
        "--solo-resumenes",
        action="store_true",
        help="Regenerar solo los resúmenes por tema (conserva tablas; usa audiencia del plan)",
    )
    parser.add_argument(
        "--solo-qc",
        action="store_true",
        help="Solo revisar tablas + PDF existentes (FinalQCAgent)",
    )
    parser.add_argument(
        "--solo-plan-accion",
        action="store_true",
        help="Generar plan de acción por rol + ensamblar PDF (requiere .md y tablas)",
    )
    parser.add_argument(
        "--sin-qc",
        action="store_true",
        help="Omitir control de calidad final tras generar el PDF",
    )
    return parser.parse_args()


def resolve_pdf_path(libro: str) -> Path:
    from src.plan_executor import resolve_book_pdf

    return resolve_book_pdf(libro)


def _run_solo_qc(slug: str) -> None:
    from src.agents.final_qc_agent import run_qc_for_slug
    sys.exit(run_qc_for_slug(slug))


def main() -> None:
    args = parse_args()
    slug = args.slug or Path(args.libro).stem.lower().replace(" ", "_")[:30]

    if args.solo_mapa:
        args.solo_enriquecer = True
        args.sin_imagenes = True
        args.sin_md = True

    if args.solo_tablas:
        args.solo_enriquecer = True
        args.sin_imagenes = True
        args.sin_md = True

    if args.solo_pdf:
        args.solo_enriquecer = True
        args.sin_imagenes = True
        args.sin_md = True

    if args.solo_intros:
        args.solo_enriquecer = True
        args.sin_imagenes = True
        args.sin_md = True

    if args.solo_plan_accion:
        args.solo_enriquecer = True
        args.sin_imagenes = True
        args.sin_md = True

    if args.solo_qc:
        if not args.slug:
            print("❌ --solo-qc requiere --slug")
            sys.exit(1)
        _run_solo_qc(args.slug)
        return

    if not args.solo_enriquecer and not args.solo_resumenes and not args.temas:
        print("❌ Debes indicar al menos un tema (o usar --solo-enriquecer / --solo-resumenes).")
        sys.exit(1)

    if not args.libro:
        print("❌ Indica el libro o la ruta al PDF.")
        sys.exit(1)

    try:
        pdf_path = resolve_pdf_path(args.libro)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        sys.exit(1)

    if not args.sin_llm and (
        args.temas
        or args.solo_resumenes
        or (args.solo_enriquecer and not args.solo_pdf)
    ):
        from src.config import RESUMENES_DIR
        from src.cost_estimator import estimar, modo_desde_main, mostrar_y_confirmar
        from src.pdf_reader import extract_text

        temas_estimacion = list(args.temas)
        if (args.solo_resumenes or args.solo_enriquecer) and not temas_estimacion:
            from src.md_loader import find_summary_md, parse_enriched_markdown

            try:
                _, resultados, _, _ = parse_enriched_markdown(
                    find_summary_md(RESUMENES_DIR / slug)
                )
                temas_estimacion = [r.tema for r in resultados]
            except FileNotFoundError:
                pass

        pdf_text = extract_text(str(pdf_path))
        estimacion = estimar(
            pdf_text,
            temas_estimacion or ["tema"],
            modo=modo_desde_main(args),
            sin_qc=args.sin_qc,
        )

        if not args.sin_confirmacion:
            if not mostrar_y_confirmar(estimacion):
                print("Cancelado.")
                sys.exit(0)
        else:
            print(
                f"📊 Costo estimado ({estimacion['modo']}): "
                f"${estimacion['costo_usd']} USD — "
                f"~{estimacion['llamadas_estimadas']} llamadas LLM — "
                f"{estimacion['tiempo_estimado_min']} min"
            )

    job = BookJob(
        pdf_path=str(pdf_path),
        temas=args.temas or [],
        max_subagentes=args.max_subagentes,
        libro_slug=slug,
        solo_enriquecer=args.solo_enriquecer,
        solo_resumenes=args.solo_resumenes,
        sin_llm=args.sin_llm,
        sin_imagenes=args.sin_imagenes,
        sin_md=args.sin_md,
        solo_mapa=args.solo_mapa,
        solo_tablas=args.solo_tablas,
        solo_pdf=args.solo_pdf,
        solo_intros=args.solo_intros,
        solo_plan_accion=args.solo_plan_accion,
        sin_qc=args.sin_qc,
    )

    output = MainAgent(max_subagentes=args.max_subagentes).process_book(job)
    print(f"\n✅ Listo. Salida en: resumenes/{output.libro_slug}/")
    if output.markdown_path:
        print(f"✅ Markdown: {output.markdown_path}")
    if output.pdf_path and output.pdf_path.exists():
        print(f"✅ PDF:      {output.pdf_path}")
    if output.package and output.package.mapa_path and output.package.mapa_path.exists():
        print(f"✅ Mapa:     {output.package.mapa_path}")


if __name__ == "__main__":
    main()

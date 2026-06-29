#!/usr/bin/env python3
"""
kdp_main.py — Pipeline de MARKETING Amazon KDP (separada de main.py).

CONSTITUCIÓN: SOLO LEE el PDF. PROHIBIDO modificarlo.
Si el PDF tiene problemas → logs/produccion_solicitudes.json → producción lo corrige.

Lee un PDF ya creado y genera listing para Amazon: título, descripción,
keywords y beneficios.

Uso:
  python kdp_main.py "resumenes/pareto/El principio de Pareto - Antoine Delers.pdf"
  python kdp_main.py --slug pareto
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import RESUMENES_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera listing Amazon KDP desde un PDF existente (pipeline de marketing)."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        default="",
        help="Ruta al PDF (absoluta o relativa al proyecto)",
    )
    parser.add_argument(
        "--slug",
        default="",
        help="Atajo: busca el PDF principal en resumenes/{slug}/",
    )
    parser.add_argument(
        "--sin-aprendizaje",
        action="store_true",
        help="No ejecutar MarketingLearningAgent al final",
    )
    parser.add_argument(
        "--sin-bot",
        action="store_true",
        help="Omitir bot Amazon (investigación de audiencia en marketplace)",
    )
    parser.add_argument(
        "--bot-headless",
        action="store_true",
        help="Bot Amazon sin ventana visible",
    )
    return parser.parse_args()


def resolve_pdf(pdf_arg: str, slug: str) -> Path:
    if pdf_arg:
        path = Path(pdf_arg)
        if not path.is_absolute():
            path = Path.cwd() / path
        if path.is_file():
            return path.resolve()
        raise FileNotFoundError(f"No encontré el PDF: {pdf_arg}")

    if slug:
        folder = RESUMENES_DIR / slug
        if not folder.is_dir():
            raise FileNotFoundError(f"No existe la carpeta: {folder}")
        candidatos = sorted(
            folder.glob("*.pdf"),
            key=lambda p: p.stat().st_size,
            reverse=True,
        )
        candidatos = [p for p in candidatos if p.stat().st_size > 50_000]
        if candidatos:
            return candidatos[0].resolve()
        raise FileNotFoundError(f"No hay PDF principal en {folder}")

    raise SystemExit(
        "Indica la ruta del PDF o usa --slug.\n"
        "Ejemplo:\n"
        '  python kdp_main.py "resumenes/pareto/El principio de Pareto - Antoine Delers.pdf"\n'
        "  python kdp_main.py --slug pareto"
    )


def main() -> None:
    args = parse_args()
    try:
        pdf_path = resolve_pdf(args.pdf, args.slug)
    except (FileNotFoundError, SystemExit) as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)

    from src.marketing.pipeline import KDPMarketingPipeline

    try:
        KDPMarketingPipeline(
            sin_aprendizaje=args.sin_aprendizaje,
            sin_bot=args.sin_bot,
            bot_headless=args.bot_headless,
        ).run(pdf_path)
        print("\n✅ Listing KDP listo para copiar en amazon.com/kdp\n")
    except RuntimeError as err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"❌ Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

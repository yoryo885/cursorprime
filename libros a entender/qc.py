#!/usr/bin/env python3
"""
qc.py — Control de calidad final (tablas + PDF).

Ejemplos:
  python qc.py --slug pareto
  python qc.py --slug pareto --sin-llm
"""
from __future__ import annotations

import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Revisa tablas y PDF antes del entregable (FinalQCAgent).",
    )
    parser.add_argument("--slug", required=True, help="Carpeta en resumenes/")
    parser.add_argument(
        "--sin-llm",
        action="store_true",
        help="Solo reglas automáticas, sin revisión Claude",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from src.agents.final_qc_agent import run_qc_for_slug

    code = run_qc_for_slug(args.slug, skip_llm=args.sin_llm)
    if code == 0:
        print(f"\n📄 Informe: resumenes/{args.slug}/meta/final_qc_report.json")
    sys.exit(code)


if __name__ == "__main__":
    main()

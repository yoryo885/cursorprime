#!/usr/bin/env python3
"""CLI — Pipeline TikTok (opcional: --fuente resumen/PDF en solo lectura)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import AGENT_ORDER  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(
        description="TikTok content pipeline — pesca ideas de un resumen/PDF (sin modificarlo) y arma el guion"
    )
    p.add_argument("--tema", default="", help="Tema del video (opcional si hay --fuente)")
    p.add_argument(
        "--fuente",
        default="",
        help="Ruta SOLO LECTURA a .md/.pdf de libros a entender (u otro resumen). No se modifica.",
    )
    p.add_argument("--nicho", default="productividad", help="Nicho / audiencia")
    p.add_argument("--producto", default="", help="Nombre de producto (opcional)")
    p.add_argument("--slug", default=None, help="Slug de salida (default: desde tema/fuente)")
    p.add_argument("--reset-checkpoint", action="store_true")
    p.add_argument("--solo", choices=AGENT_ORDER, help="Correr solo un agente")
    p.add_argument("--desde", choices=AGENT_ORDER, help="Reanudar desde un agente")
    args = p.parse_args()

    if not args.tema and not args.fuente:
        p.error("Indica --tema y/o --fuente")

    state = run_pipeline(
        tema=args.tema or "desde_fuente",
        slug=args.slug,
        nicho=args.nicho,
        producto=args.producto,
        fuente=args.fuente,
        reset=args.reset_checkpoint,
        solo=args.solo,
        desde=args.desde,
    )
    qa = state.get("qa") or {}
    fe = state.get("fuente_extract") or {}
    if fe:
        print(f"Fuente (solo lectura): {fe.get('fuente_path') or '—'}")
        print(f"Ideas pescadas: {len(state.get('ideas_centrales') or [])}")
    print(f"QA score: {qa.get('score')} · ok={qa.get('ok')}")
    if qa.get("regenerar"):
        print(f"Regenerar: {', '.join(qa['regenerar'])}")


if __name__ == "__main__":
    main()

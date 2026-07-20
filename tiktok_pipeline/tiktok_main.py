#!/usr/bin/env python3
"""CLI — Pipeline TikTok (hook → script → shotlist → QA)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import AGENT_ORDER  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="TikTok content pipeline — agentes + skills")
    p.add_argument("--tema", required=True, help="Tema o producto del video")
    p.add_argument("--nicho", default="productividad", help="Nicho / audiencia")
    p.add_argument("--producto", default="", help="Nombre de producto (opcional)")
    p.add_argument("--slug", default=None, help="Slug de salida (default: desde tema)")
    p.add_argument("--reset-checkpoint", action="store_true")
    p.add_argument("--solo", choices=AGENT_ORDER, help="Correr solo un agente")
    p.add_argument("--desde", choices=AGENT_ORDER, help="Reanudar desde un agente")
    args = p.parse_args()

    state = run_pipeline(
        tema=args.tema,
        slug=args.slug,
        nicho=args.nicho,
        producto=args.producto,
        reset=args.reset_checkpoint,
        solo=args.solo,
        desde=args.desde,
    )
    qa = state.get("qa") or {}
    print(f"QA score: {qa.get('score')} · ok={qa.get('ok')}")
    if qa.get("regenerar"):
        print(f"Regenerar: {', '.join(qa['regenerar'])}")


if __name__ == "__main__":
    main()

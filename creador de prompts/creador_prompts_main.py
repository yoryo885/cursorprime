#!/usr/bin/env python3
"""CLI — Creador de Prompts (compartido para todos los proyectos)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_SLUG, load_json, slugify  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def load_solicitud(path: Path | None, slug: str) -> tuple[dict, str]:
    if path:
        data = load_json(path, {}) or {}
        return data, slug or slugify(str(data.get("titulo") or path.stem))
    default = ROOT / "data" / slug / "inputs" / "solicitud.json"
    if default.exists():
        return load_json(default, {}) or {}, slug or DEFAULT_SLUG
    raise SystemExit(f"No hay solicitud en data/{slug}/inputs/solicitud.json")


def main() -> None:
    p = argparse.ArgumentParser(description="Creador de Prompts — cursorprime")
    p.add_argument("--slug", default=DEFAULT_SLUG)
    p.add_argument("--solicitud", help="Ruta a solicitud.json")
    p.add_argument(
        "--tipo",
        choices=["imagen", "copy", "cursor", "pipeline", "marketing", "evaluacion", "animacion"],
        help="Tipo de prompt (sobreescribe solicitud)",
    )
    p.add_argument("--proyecto", help="ID del proyecto destino (meta/proyectos.json)")
    p.add_argument("--reset-checkpoint", action="store_true")
    args = p.parse_args()

    sol_path = Path(args.solicitud) if args.solicitud else None
    solicitud, slug = load_solicitud(sol_path, args.slug)

    if args.tipo:
        solicitud = {**solicitud, "tipo": args.tipo}
    if args.proyecto:
        solicitud = {**solicitud, "proyecto_destino": args.proyecto}

    dest = ROOT / "data" / slug / "inputs" / "solicitud.json"
    if sol_path or not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(solicitud, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✏️  Creador de Prompts — {slug}")
    print(f"   Tipo: {solicitud.get('tipo', '?')} → {solicitud.get('proyecto_destino', 'general')}\n")

    ok = run_pipeline(slug=slug, solicitud=solicitud, reset=args.reset_checkpoint)
    if ok:
        print(f"\n✅ Listo: data/{slug}/output/\n")
    else:
        print("\n❌ Falló — logs/errores.json\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

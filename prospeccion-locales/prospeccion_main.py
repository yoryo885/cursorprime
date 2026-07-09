#!/usr/bin/env python3
"""CLI — Bot prospección clientes locales (Paso 0 Presencia digital)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import DATA_DIR, places_api_key, save_json  # noqa: E402
from src.mock_data import mock_leads  # noqa: E402
from src.places import search_places  # noqa: E402
from src.render import build_payload, render_md  # noqa: E402
from src.score import score_lead  # noqa: E402


def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60] or "busqueda"


def cmd_buscar(args) -> int:
    rubro = args.rubro.strip()
    ciudad = args.ciudad.strip()
    slug = args.slug or _slugify(f"{rubro}-{ciudad}")
    limit = args.limit

    if args.mock:
        raw = mock_leads(rubro, ciudad, limit=limit)
        modo = "mock"
    elif places_api_key():
        query = f"{rubro} en {ciudad}, Chile"
        print(f"🔍 Places API: {query}\n")
        raw = search_places(query, places_api_key(), limit=limit)
        modo = "places"
    else:
        if args.places:
            print("❌ Falta GOOGLE_PLACES_API_KEY en .env")
            return 1
        print("⚠️  Sin GOOGLE_PLACES_API_KEY — usando modo mock")
        raw = mock_leads(rubro, ciudad, limit=limit)
        modo = "mock"

    scored = [score_lead(L) for L in raw]
    payload = build_payload(rubro, ciudad, modo, scored)

    out_dir = DATA_DIR / slug / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "leads.json", payload)
    (out_dir / "leads.md").write_text(render_md(payload), encoding="utf-8")

    print(f"✅ {payload['viables']} viables / {payload['total']} leads")
    print(f"   → data/{slug}/output/leads.json")
    print(f"   → data/{slug}/output/leads.md\n")
    for L in payload["leads"][:5]:
        flag = "✓" if L["viable"] else "·"
        print(f"   {flag} [{L['score']}] {L['nombre']} — {', '.join(L['senales'])}")
    return 0


def cmd_resumen(args) -> int:
    slug = args.slug
    path = DATA_DIR / slug / "output" / "leads.json"
    if not path.exists():
        print(f"No hay leads para slug '{slug}'. Corre: buscar --rubro X --ciudad Y")
        return 1
    from src.config import load_json

    p = load_json(path, {})
    print(f"{p.get('rubro')} · {p.get('ciudad')} — {p.get('viables')}/{p.get('total')} viables ({p.get('modo')})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Prospección locales — candidatos Presencia digital")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("buscar", help="Buscar negocios y puntuar viabilidad")
    b.add_argument("--rubro", required=True, help="Ej: dentista, restaurante, ferretería")
    b.add_argument("--ciudad", required=True, help="Ej: Providencia, Santiago")
    b.add_argument("--slug", help="Carpeta salida data/{slug}")
    b.add_argument("--limit", type=int, default=10, help="Máximo resultados")
    b.add_argument("--mock", action="store_true", help="Datos demo sin API")
    b.add_argument("--places", action="store_true", help="Forzar Places API (requiere .env)")
    b.set_defaults(func=cmd_buscar)

    r = sub.add_parser("resumen", help="Resumen de una búsqueda guardada")
    r.add_argument("--slug", required=True)
    r.set_defaults(func=cmd_resumen)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

"""00 — Referencia visual: patrones estructurales de URLs curadas (sin scraping libre)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG = Path(__file__).resolve().parents[1] / "config" / "referencias.json"

# Patrones estructurales derivados de la lista curada (no copy literal)
PATRONES_BASE = {
    "trust_badge_posicion": "arriba del todo, antes del hero",
    "hero_visual": "imagen real de producto, nunca texto duplicado",
    "testimonio_formato": "quote corto + nombre + ciudad entre paréntesis",
    "cta_por_bloque": "un único CTA claro por bloque, no botones compitiendo",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    """
    Lee src/config/referencias.json (curado a mano).
    Devuelve referencia.json con patrones estructurales — nunca copia texto/diseño.
    """
    urls: list[str] = []
    if CONFIG.exists():
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        urls = list(data.get("urls") or [])
    if not urls:
        urls = ["https://filjos.com/"]

    # override opcional desde input (sigue siendo lista curada, no scrape)
    extra = input.get("referencias_urls") or []
    for u in extra:
        if u and u not in urls:
            urls.append(u)

    return {
        **PATRONES_BASE,
        "fuente": urls,
    }

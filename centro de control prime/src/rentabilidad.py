"""Ranking de rentabilidad — ideas de proyectos."""

from __future__ import annotations

from src.config import CURSORPRIME, load_json

RANKING_PATH = CURSORPRIME / "ideas de proyectos" / "RANKING_RENTABILIDAD.json"


def load_rentabilidad() -> dict:
    data = load_json(RANKING_PATH, {}) or {}
    if not data.get("ranking"):
        return {}
    return data

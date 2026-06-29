"""Backend web — mock MVP; V1 pytrends + Playwright competition."""

from __future__ import annotations

from datetime import datetime, timezone

from src.web_competition import fetch_competition
from src.web_trends import fetch_trends


def mock_source(url: str, title: str) -> dict:
    return {"url": url, "title": title, "accessed_at": datetime.now(timezone.utc).isoformat(), "mock": True}


def search_trends(keywords: list[str], mock: bool = True, mercado: str = "CL") -> dict:
    return fetch_trends(keywords, mercado=mercado, mock=mock)


def search_market(idea: dict, mock: bool = True) -> dict:
    """Market sigue heurístico — pendiente V1.5 (APIs / informes)."""
    mercado = idea.get("mercado") or "CL"
    base = {
        "tam_usd": {"min": 1_000_000, "max": 50_000_000, "point": 8_000_000},
        "crecimiento_anual_pct": {"min": 3, "max": 18, "point": 8},
        "demanda_score": {"min": 4, "max": 8, "point": 6},
        "mercado": mercado,
    }
    if mock:
        return {
            **base,
            "sources": [mock_source(f"https://example.com/market-{mercado}", f"Mercado {mercado} (mock)")],
            "mock": True,
            "warnings": ["market aún heurístico — V1.5 pendiente"],
        }
    return {
        **base,
        "sources": [mock_source(f"https://www.google.com/search?q=mercado+{mercado}", f"Búsqueda mercado {mercado}")],
        "mock": True,
        "warnings": ["market aún heurístico — solo trend/competition son web real en V1"],
    }


def search_competition(idea: dict, mock: bool = True, filters: dict | None = None) -> dict:
    return fetch_competition(idea, mock=mock, filters=filters)

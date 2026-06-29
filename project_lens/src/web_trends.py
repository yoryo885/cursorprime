"""Google Trends vía pytrends — V1 web real."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

GEO_MAP = {"CL": "CL", "CHILE": "CL", "MX": "MX", "MEXICO": "MX", "US": "US", "USA": "US", "AR": "AR", "CO": "CO", "PE": "PE"}


def _source(keyword: str, geo: str, mock: bool) -> dict:
    url = f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}&geo={geo}"
    return {
        "url": url,
        "title": f"Google Trends: {keyword}" + (f" ({geo})" if geo else ""),
        "accessed_at": datetime.now(timezone.utc).isoformat(),
        "mock": mock,
    }


def _direction(values: list[float]) -> str:
    if len(values) < 4:
        return "estable"
    mid = len(values) // 2
    older = sum(values[:mid]) / max(mid, 1)
    recent = sum(values[mid:]) / max(len(values) - mid, 1)
    if recent > older * 1.12:
        return "subiendo"
    if recent < older * 0.88:
        return "muriendo"
    return "estable"


def _interest_series(pytrends, keyword: str, geo: str) -> tuple[list[float], str]:
    """Devuelve serie de interés y geo usado."""
    attempts = [(geo, keyword)]
    if geo:
        attempts.append(("", keyword))
    # Keyword más corta si la frase es larga
    parts = keyword.split()
    if len(parts) > 2:
        attempts.append((geo, " ".join(parts[:2])))
        if geo:
            attempts.append(("", " ".join(parts[:2])))

    last_err = "sin datos"
    for g, kw in attempts:
        try:
            pytrends.build_payload([kw[:100]], cat=0, timeframe="today 12-m", geo=g, gprop="")
            df = pytrends.interest_over_time()
            if df is None or df.empty or kw not in df.columns:
                last_err = f"vacío para '{kw}' geo={g or 'world'}"
                continue
            if "isPartial" in df.columns:
                df = df[df["isPartial"] == False]  # noqa: E712
            series = [float(x) for x in df[kw].tolist() if x == x]
            if series and max(series) > 0:
                return series, g or "world"
            last_err = f"serie cero para '{kw}' geo={g or 'world'}"
        except Exception as exc:
            last_err = str(exc)
    raise ValueError(last_err)


def fetch_trends(keywords: list[str], mercado: str = "CL", mock: bool = True) -> dict:
    kw = [k.strip() for k in keywords if k and k.strip()][:5] or ["mercado"]
    geo = GEO_MAP.get((mercado or "CL").upper(), "CL")

    if mock:
        score = 6 if any(len(k) > 4 for k in kw) else 4
        return {
            "keywords": kw,
            "geo": geo,
            "direccion": "estable" if score >= 5 else "muriendo",
            "trend_score": score,
            "interest_avg": score * 10,
            "interest_by_keyword": {k: score * 10 for k in kw[:3]},
            "sources": [_source(kw[0], geo, mock=True)],
            "mock": True,
            "warnings": ["datos mock"],
        }

    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="es", tz=360, timeout=(10, 25))
        primary = kw[0][:100]
        series, geo_used = _interest_series(pytrends, primary, geo)

        avg = sum(series) / len(series)
        direction = _direction(series)
        score = max(1.0, min(10.0, round(avg / 10, 1)))

        interest_by_kw = {primary: round(avg, 1)}
        if len(kw) > 1:
            try:
                s2, _ = _interest_series(pytrends, kw[1][:100], geo)
                interest_by_kw[kw[1]] = round(sum(s2) / len(s2), 1)
            except Exception as exc:
                logger.warning("pytrends keyword secundaria: %s", exc)

        return {
            "keywords": kw,
            "geo": geo_used,
            "direccion": direction,
            "trend_score": score,
            "interest_avg": round(avg, 1),
            "interest_by_keyword": interest_by_kw,
            "sources": [_source(primary, geo_used if geo_used != "world" else "", mock=False)],
            "mock": False,
            "warnings": ["geo worldwide"] if geo_used == "world" and geo else [],
        }
    except Exception as exc:
        logger.warning("pytrends falló (%s) — fallback mock", exc)
        score = 5.0
        return {
            "keywords": kw,
            "geo": geo,
            "direccion": "estable",
            "trend_score": score,
            "interest_avg": 50.0,
            "interest_by_keyword": {kw[0]: 50.0},
            "sources": [_source(kw[0], geo, mock=True)],
            "mock": True,
            "warnings": [f"pytrends no disponible: {exc}"],
        }

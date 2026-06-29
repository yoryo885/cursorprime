"""Helpers compartidos para agentes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def metric(min_v: float, max_v: float, point: float | None = None) -> dict[str, float]:
    p = point if point is not None else (min_v + max_v) / 2
    return {"min": round(min_v, 2), "max": round(max_v, 2), "point": round(p, 2)}


def envelope(
    agent: str,
    confidence: float,
    error_margin_pct: float,
    metrics: dict | None = None,
    findings: list | None = None,
    sources: list | None = None,
    warnings: list | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    out = {
        "agent": agent,
        "confidence": round(confidence, 2),
        "error_margin_pct": error_margin_pct,
        "sources": sources or [],
        "findings": findings or [],
        "metrics": metrics or {},
        "warnings": warnings or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        out.update(extra)
    return out


def tipo_negocio(idea: dict) -> str:
    explicit = (idea.get("tipo_negocio") or idea.get("tipo") or "").lower()
    if explicit in ("saas", "ecommerce", "marketplace", "servicio"):
        return explicit
    texto = " ".join(str(idea.get(k) or "") for k in ("modelo_negocio", "problema", "titulo")).lower()
    if any(w in texto for w in ("saas", "software", "suscripcion", "plataforma")):
        return "saas"
    if "marketplace" in texto:
        return "marketplace"
    if any(w in texto for w in ("whatsapp", "bot", "local", "servicio", "pyme")):
        return "servicio"
    if any(w in texto for w in ("ecommerce", "dropship", "mercado libre", "tienda online")):
        return "ecommerce"
    return "saas"

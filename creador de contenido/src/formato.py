"""Formato de video: promo (venta) vs ensenanza (didáctico / canal estilo Psicología Invisible)."""

from __future__ import annotations


def formato_video(lote: dict, context: dict | None = None) -> str:
    """Devuelve 'ensenanza' | 'promo'."""
    ctx = context or {}
    raw = (
        lote.get("formato")
        or lote.get("estilo_video")
        or (lote.get("video") or {}).get("formato")
        or ctx.get("formato")
        or ""
    )
    raw = str(raw).strip().lower()
    if raw in ("ensenanza", "enseñanza", "teaching", "educativo", "didactico", "didáctico"):
        return "ensenanza"
    if raw in ("promo", "venta", "marketing"):
        return "promo"
    # Receta ensenanza fuerza el formato
    receta = str(lote.get("receta") or ctx.get("receta") or "").lower()
    if receta in ("ensenanza", "enseñanza"):
        return "ensenanza"
    return "promo"

"""Utilidades de copy: sanitizar concatenaciones y naming público."""

from __future__ import annotations

import re


def sanitize_prepend(prefix: str, value: str) -> str:
    """
    Antepone `prefix` solo si `value` no lo trae ya.
    Evita "desde desde $4.99".
    """
    value = (value or "").strip()
    prefix = (prefix or "").strip()
    if not value:
        return prefix
    if not prefix:
        return value
    low = value.lower()
    pre = prefix.lower()
    if low.startswith(pre + " ") or low == pre or low.startswith(pre):
        # ya incluye el prefijo (con o sin espacio)
        return value
    return f"{prefix} {value}"


def collapse_duplicate_words(text: str) -> str:
    """Colapsa palabras consecutivas repetidas (case-insensitive)."""
    return re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)


def public_name(brief: dict) -> str:
    """Nombre visible: nombre_producto > marca > producto."""
    return (
        (brief.get("nombre_producto") or brief.get("marca") or brief.get("producto") or "")
        .strip()
    )


def propuesta(brief: dict) -> str:
    return (brief.get("propuesta_valor") or brief.get("promesa") or "").strip()

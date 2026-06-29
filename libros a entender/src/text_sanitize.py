"""Limpieza de artefactos markdown en textos de resumen."""
from __future__ import annotations

import re

_RESUMEN_HEADING = re.compile(r"^#{1,3}\s*Resumen\s*$", re.IGNORECASE | re.MULTILINE)


def clean_resumen_markdown(text: str) -> str:
    """Quita encabezados sueltos «## Resumen» que no deben verse en el PDF."""
    if not text:
        return ""
    cleaned = _RESUMEN_HEADING.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()

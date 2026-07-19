"""Aprendizaje continuo: registra mejoras y las reinyecta al brief."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json

MEJORAS_PATH = ROOT / "logs" / "mejoras.json"


def load_mejoras() -> dict:
    data = load_json(MEJORAS_PATH, None)
    if not data:
        return {"version": 1, "mejoras": []}
    return data


def registrar_mejora(mensaje: str, cambio: str, aplicado: bool = True) -> dict:
    data = load_mejoras()
    mejoras = data.setdefault("mejoras", [])
    entry = {
        "id": f"m{len(mejoras) + 1:03d}",
        "at": datetime.now(timezone.utc).isoformat(),
        "mensaje": mensaje,
        "cambio": cambio,
        "aplicado": aplicado,
    }
    mejoras.append(entry)
    save_json(MEJORAS_PATH, data)
    return entry


def reglas_activas() -> list[str]:
    """Frases cortas que el brief/build deben respetar."""
    out = []
    for m in load_mejoras().get("mejoras", []):
        if m.get("aplicado") and m.get("cambio"):
            out.append(str(m["cambio"]))
    return out


def aplicar_al_brief(brief: dict) -> dict:
    brief = dict(brief)
    brief["aprendizaje"] = reglas_activas()
    # Regla fija actual: siempre catálogo multi-producto si hay productos
    if brief.get("productos"):
        brief["mostrar_catalogo"] = True
    return brief

"""Aprendizaje continuo: registra mejoras y las aplica al brief (efecto real en HTML)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json

MEJORAS_PATH = ROOT / "logs" / "mejoras.json"

# Lista cerrada de efectos que html_builder / brief entienden
EFECTOS_CONOCIDOS = (
    "ocultar_newsletter",
    "forzar_cta",
    "ocultar_faq",
)


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
        "efectos": _parse_efectos(mensaje, cambio),
    }
    mejoras.append(entry)
    save_json(MEJORAS_PATH, data)
    return entry


def _parse_efectos(mensaje: str, cambio: str) -> dict:
    """Traduce texto libre a flags que el builder respeta."""
    text = f"{mensaje} {cambio}".lower()
    efectos: dict = {}
    if any(x in text for x in ("quitar newsletter", "ocultar newsletter", "sin newsletter", "no newsletter")):
        efectos["ocultar_newsletter"] = True
    if any(x in text for x in ("quitar faq", "ocultar faq", "sin faq")):
        efectos["ocultar_faq"] = True
    m = re.search(r"cta\s*[:=]\s*[\"']?([^\"'\n]+)[\"']?", text, re.I)
    if m:
        efectos["forzar_cta"] = m.group(1).strip()
    elif "cambiar cta" in text or "cta a " in text:
        m2 = re.search(r"(?:cta a|cambiar cta(?: a)?)\s+(.+)$", text)
        if m2:
            efectos["forzar_cta"] = m2.group(1).strip()
    return efectos


def reglas_activas() -> list[str]:
    """Frases cortas que el brief/build deben respetar."""
    out = []
    for m in load_mejoras().get("mejoras", []):
        if m.get("aplicado") and m.get("cambio"):
            out.append(str(m["cambio"]))
    return out


def efectos_activos() -> dict:
    """Merge de efectos de mejoras aplicadas (última gana por clave)."""
    merged: dict = {}
    for m in load_mejoras().get("mejoras", []):
        if not m.get("aplicado"):
            continue
        efectos = m.get("efectos") or _parse_efectos(m.get("mensaje") or "", m.get("cambio") or "")
        merged.update(efectos)
    return merged


def aplicar_al_brief(brief: dict) -> dict:
    brief = dict(brief)
    brief["aprendizaje"] = reglas_activas()
    efectos = efectos_activos()
    brief["efectos_aprendizaje"] = efectos
    if efectos.get("ocultar_newsletter"):
        brief["ocultar_newsletter"] = True
    if efectos.get("ocultar_faq"):
        brief["ocultar_faq"] = True
    if efectos.get("forzar_cta"):
        brief["cta"] = str(efectos["forzar_cta"])
    # Regla fija: mostrar catálogo si hay productos
    if brief.get("productos"):
        brief["mostrar_catalogo"] = True
    return brief

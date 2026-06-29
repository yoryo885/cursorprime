"""Gestión de cola — aprobar / rechazar / listar."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import (
    COLA_APROBADAS,
    COLA_EN_ESPERA,
    COLA_PENDIENTES,
    COLA_RECHAZADAS,
    load_json,
    save_json,
)


def listar_cola() -> dict:
    def _items(folder: Path, *, skip: set[str] | None = None) -> list[dict]:
        if not folder.exists():
            return []
        out = []
        for p in sorted(folder.glob("idea-*.json")):
            if p.name == "prioridad.json":
                continue
            data = load_json(p, {}) or {}
            if skip and data.get("estado") in skip:
                continue
            data["_path"] = str(p)
            out.append(data)
        return out

    todas_aprobadas = _items(COLA_APROBADAS)
    implementadas = [i for i in todas_aprobadas if i.get("estado") == "implementada"]
    aprobadas = [i for i in todas_aprobadas if i.get("estado") != "implementada"]

    return {
        "pendientes": _items(COLA_PENDIENTES),
        "en_espera": _items(COLA_EN_ESPERA),
        "aprobadas": aprobadas,
        "implementadas": implementadas,
        "rechazadas": _items(COLA_RECHAZADAS),
    }


def aprobar(idea_id: str, nota: str = "") -> dict:
    src = COLA_PENDIENTES / f"{idea_id}.json"
    if not src.exists():
        return {"ok": False, "error": f"No encontrada en pendientes: {idea_id}"}

    idea = load_json(src, {}) or {}
    idea["estado"] = "aprobada"
    idea["aprobada_at"] = datetime.now(timezone.utc).isoformat()
    if nota:
        idea["nota_usuario"] = nota

    COLA_APROBADAS.mkdir(parents=True, exist_ok=True)
    save_json(COLA_APROBADAS / f"{idea_id}.json", idea)
    src.unlink()

    try:
        from src.bridge_ideas import exportar_idea

        exportar_idea(idea, evaluar=False)
    except Exception:
        pass

    return {"ok": True, "idea": idea}


def posponer(idea_id: str, nota: str = "") -> dict:
    """Guarda sin rechazar — revisar después."""
    src = COLA_PENDIENTES / f"{idea_id}.json"
    if not src.exists():
        return {"ok": False, "error": f"No encontrada en pendientes: {idea_id}"}

    idea = load_json(src, {}) or {}
    idea["estado"] = "en_espera"
    idea["pospuesta_at"] = datetime.now(timezone.utc).isoformat()
    if nota:
        idea["nota_usuario"] = nota

    COLA_EN_ESPERA.mkdir(parents=True, exist_ok=True)
    save_json(COLA_EN_ESPERA / f"{idea_id}.json", idea)
    src.unlink()
    return {"ok": True, "idea": idea}


def rechazar(idea_id: str, motivo: str = "") -> dict:
    src = COLA_PENDIENTES / f"{idea_id}.json"
    if not src.exists():
        return {"ok": False, "error": f"No encontrada en pendientes: {idea_id}"}

    idea = load_json(src, {}) or {}
    idea["estado"] = "rechazada"
    idea["rechazada_at"] = datetime.now(timezone.utc).isoformat()
    idea["motivo_rechazo"] = motivo or "sin motivo"

    COLA_RECHAZADAS.mkdir(parents=True, exist_ok=True)
    save_json(COLA_RECHAZADAS / f"{idea_id}.json", idea)
    src.unlink()
    return {"ok": True, "idea": idea}

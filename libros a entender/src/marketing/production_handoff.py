"""
Handoff marketing → producción.

Si marketing detecta un problema en el PDF, NO lo corrige:
registra una solicitud para que main.py / agentes de producción actúen.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import PRODUCCION_SOLICITUDES_LOG
from src.marketing.constitution import assert_output_path_allowed


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> list[dict]:
    path = assert_output_path_allowed(PRODUCCION_SOLICITUDES_LOG)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save(items: list[dict]) -> None:
    path = assert_output_path_allowed(PRODUCCION_SOLICITUDES_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def infer_slug_from_pdf(pdf_path: Path) -> str:
    parts = Path(pdf_path).resolve().parts
    if "resumenes" in parts:
        idx = parts.index("resumenes")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return Path(pdf_path).parent.name


def crear_solicitud(
    *,
    pdf_origen: str | Path,
    problema: str,
    solicitud: str,
    tipo: str = "contenido",
    prioridad: str = "media",
    agente_destino: str = "main_agent",
    contexto: dict[str, Any] | None = None,
) -> dict:
    pdf_path = Path(pdf_origen).resolve()
    entry = {
        "id": f"sol-{_now_iso().replace(':', '').replace('+', '')[:17]}",
        "timestamp": _now_iso(),
        "estado": "pendiente",
        "origen": "marketing",
        "pdf_origen": str(pdf_path),
        "slug": infer_slug_from_pdf(pdf_path),
        "tipo": tipo,
        "prioridad": prioridad,
        "problema": problema.strip(),
        "solicitud": solicitud.strip(),
        "agente_destino": agente_destino,
        "contexto": contexto or {},
    }
    items = _load()
    items.append(entry)
    _save(items)
    return entry


def solicitudes_pendientes(slug: str = "") -> list[dict]:
    items = _load()
    pendientes = [i for i in items if i.get("estado") == "pendiente"]
    if slug:
        pendientes = [i for i in pendientes if i.get("slug") == slug]
    return pendientes

"""Aprendizaje acumulado de la pipeline de marketing KDP."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import MARKETING_ERRORES_LOG, MARKETING_MEJORAS_LOG


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _default_mejoras() -> dict:
    return {
        "instrucciones_globales": [],
        "prompts_agentes": {
            "contenido": [],
            "titulo": [],
            "descripcion": [],
            "keywords": [],
        },
        "historial": [],
    }


def _normalize(data: dict) -> dict:
    default = _default_mejoras()
    if not isinstance(data, dict):
        return default
    prompts = data.get("prompts_agentes")
    if not isinstance(prompts, dict):
        prompts = default["prompts_agentes"]
    return {
        "instrucciones_globales": data.get("instrucciones_globales", []),
        "prompts_agentes": {**default["prompts_agentes"], **prompts},
        "historial": data.get("historial", []),
    }


AGENTE_KEYS = ("contenido", "titulo", "descripcion", "keywords")


class MarketingLearningSystem:
    """Registra fallos de QC y acumula mejoras entre listings."""

    def __init__(self) -> None:
        self._session_events: list[dict] = []

    def instrucciones_globales(self) -> list[str]:
        data = _normalize(_load_json(MARKETING_MEJORAS_LOG, _default_mejoras()))
        return [str(i) for i in data.get("instrucciones_globales", []) if i]

    def instrucciones_agente(self, agente: str) -> list[str]:
        if agente not in AGENTE_KEYS:
            return []
        data = _normalize(_load_json(MARKETING_MEJORAS_LOG, _default_mejoras()))
        bucket = data.get("prompts_agentes", {}).get(agente, [])
        return [str(p) for p in bucket if p]

    def instrucciones_para(self, agente: str) -> list[str]:
        return self.instrucciones_globales() + self.instrucciones_agente(agente)

    def load_all(self) -> dict:
        return _normalize(_load_json(MARKETING_MEJORAS_LOG, _default_mejoras()))

    def log_qc_run(
        self,
        *,
        pdf_origen: str,
        titulo: str,
        score: float,
        issues: list[str],
        warnings: list[str],
    ) -> None:
        entry = {
            "timestamp": _now_iso(),
            "pdf_origen": pdf_origen,
            "titulo": titulo,
            "tipo": "qc_listing",
            "score": score,
            "issues": issues,
            "warnings": warnings,
        }
        self._session_events.append(entry)
        log = _load_json(MARKETING_ERRORES_LOG, [])
        if isinstance(log, list):
            log.append(entry)
            _save_json(MARKETING_ERRORES_LOG, log)

    def log_metricas(
        self,
        *,
        asin: str = "",
        titulo: str = "",
        ventas: int | None = None,
        bsr: int | None = None,
        notas: str = "",
    ) -> None:
        """Registro manual/futuro de performance en Amazon (para aprendizaje comercial)."""
        path = MARKETING_ERRORES_LOG.parent / "marketing_metricas.json"
        log = _load_json(path, [])
        if not isinstance(log, list):
            log = []
        log.append({
            "timestamp": _now_iso(),
            "asin": asin,
            "titulo": titulo,
            "ventas": ventas,
            "bsr": bsr,
            "notas": notas,
        })
        _save_json(path, log)

    def metricas_recientes(self, limit: int = 10) -> list[dict]:
        path = MARKETING_ERRORES_LOG.parent / "marketing_metricas.json"
        log = _load_json(path, [])
        if not isinstance(log, list):
            return []
        return log[-limit:]

    def save_improvements(
        self,
        *,
        pdf_origen: str,
        titulo: str,
        nuevas: dict,
    ) -> list[str]:
        data = _normalize(_load_json(MARKETING_MEJORAS_LOG, _default_mejoras()))
        aplicadas: list[str] = []

        for instruccion in nuevas.get("instrucciones_globales", []):
            s = str(instruccion).strip()
            if s and s not in data["instrucciones_globales"]:
                data["instrucciones_globales"].append(s)
                aplicadas.append(s)

        for agente, prompts in nuevas.get("prompts_agentes", {}).items():
            if agente not in AGENTE_KEYS:
                continue
            bucket = data["prompts_agentes"].setdefault(agente, [])
            for p in prompts:
                s = str(p).strip()
                if s and s not in bucket:
                    bucket.append(s)
                    aplicadas.append(f"[{agente}] {s}")

        data.setdefault("historial", []).append({
            "timestamp": _now_iso(),
            "pdf_origen": pdf_origen,
            "titulo": titulo,
            "mejoras_globales": nuevas.get("instrucciones_globales", []),
            "mejoras_agentes": nuevas.get("prompts_agentes", {}),
            "eventos_analizados": len(self._session_events),
        })
        _save_json(MARKETING_MEJORAS_LOG, data)
        return aplicadas

    def session_events(self) -> list[dict]:
        return list(self._session_events)

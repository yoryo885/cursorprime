import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.config import ERRORES_LOG, MEJORAS_LOG, POOR_SUMMARY_MIN_LENGTH
from src.llm import LLMClient
from src.models import TopicResult

ENGLISH_MIXED_PATTERN = re.compile(
    r"\b(understanding|function|however|also|because|which|"
    r"argument|describe|destaca|juga)\b",
    re.IGNORECASE,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _default_mejoras() -> dict:
    return {
        "instrucciones": [],
        "prompts_agentes": {
            "tablas": [],
            "mapa": [],
            "imagenes": [],
            "pdf": [],
        },
        "historial": [],
    }


def _normalize_mejoras(data) -> dict:
    if not isinstance(data, dict):
        return _default_mejoras()
    default = _default_mejoras()
    prompts = data.get("prompts_agentes")
    if not isinstance(prompts, dict):
        prompts = default["prompts_agentes"]
    return {
        "instrucciones": data.get("instrucciones", []),
        "prompts_agentes": {**default["prompts_agentes"], **prompts},
        "historial": data.get("historial", []),
    }


class LearningSystem:
    """Registra errores, evalúa calidad y acumula mejoras entre libros."""

    def __init__(self):
        self._session_errors: list[dict] = []

    def load_instructions(self) -> list[str]:
        data = _normalize_mejoras(_load_json(MEJORAS_LOG, _default_mejoras()))
        return data.get("instrucciones", [])

    def load_all_prompts(self) -> dict:
        data = _normalize_mejoras(_load_json(MEJORAS_LOG, _default_mejoras()))
        return {
            "instrucciones": data.get("instrucciones", []),
            **data.get("prompts_agentes", {}),
        }

    def save_agent_improvements(
        self,
        libro_slug: str,
        libro_nombre: str,
        nuevas: dict,
    ) -> None:
        data = _normalize_mejoras(_load_json(MEJORAS_LOG, _default_mejoras()))

        for instruccion in nuevas.get("instrucciones", []):
            if instruccion not in data["instrucciones"]:
                data["instrucciones"].append(instruccion)

        for agente, prompts in nuevas.get("prompts_agentes", {}).items():
            bucket = data["prompts_agentes"].setdefault(agente, [])
            for p in prompts:
                if p not in bucket:
                    bucket.append(p)

        data.setdefault("historial", []).append({
            "timestamp": _now_iso(),
            "libro_slug": libro_slug,
            "libro": libro_nombre,
            "mejoras_globales": nuevas.get("instrucciones", []),
            "mejoras_agentes": nuevas.get("prompts_agentes", {}),
        })
        _save_json(MEJORAS_LOG, data)

    def log_failure(
        self,
        libro_slug: str,
        libro_nombre: str,
        tema: str,
        subagente_id: int,
        detalle: str,
        tipo: str = "fallo",
    ) -> None:
        entry = {
            "timestamp": _now_iso(),
            "libro_slug": libro_slug,
            "libro": libro_nombre,
            "subagente_id": subagente_id,
            "tema": tema,
            "tipo": tipo,
            "detalle": detalle,
            "razones": [],
        }
        self._session_errors.append(entry)
        self._append_to_log(ERRORES_LOG, entry)

    def log_poor_summary(
        self,
        libro_slug: str,
        libro_nombre: str,
        result: TopicResult,
        razones: list[str],
    ) -> None:
        entry = {
            "timestamp": _now_iso(),
            "libro_slug": libro_slug,
            "libro": libro_nombre,
            "subagente_id": result.subagente_id,
            "tema": result.tema,
            "tipo": "resumen_pobre",
            "detalle": result.resumen[:300],
            "razones": razones,
        }
        self._session_errors.append(entry)
        self._append_to_log(ERRORES_LOG, entry)

    def evaluate_result(self, result: TopicResult) -> list[str]:
        """Detecta señales de un resumen de baja calidad."""
        issues = []
        resumen = result.resumen.strip()

        if len(resumen) < POOR_SUMMARY_MIN_LENGTH:
            issues.append("resumen_muy_corto")
        if not result.fragmentos:
            issues.append("sin_fragmentos")
        if "no se encontró" in resumen.lower():
            issues.append("sin_informacion_relevante")
        if ENGLISH_MIXED_PATTERN.search(resumen):
            issues.append("mezcla_idiomas")
        if resumen.count(".") < 2:
            issues.append("resumen_poco_estructurado")

        return issues

    def review_and_improve(
        self,
        llm: LLMClient,
        libro_slug: str,
        libro_nombre: str,
    ) -> list[str]:
        """
        Tras procesar un libro, analiza errores de la sesión y genera
        mejoras de instrucciones para el siguiente libro.
        """
        session_errors = [
            e for e in self._session_errors if e["libro_slug"] == libro_slug
        ]
        if not session_errors:
            return []

        data = _normalize_mejoras(_load_json(MEJORAS_LOG, _default_mejoras()))
        current = data.get("instrucciones", [])
        nuevas = llm.generate_improvements(
            errores=session_errors,
            instrucciones_actuales=current,
            libro_nombre=libro_nombre,
        )

        if not nuevas:
            return []

        merged = list(current)
        for instruccion in nuevas:
            if instruccion not in merged:
                merged.append(instruccion)

        data["instrucciones"] = merged
        data.setdefault("historial", []).append(
            {
                "timestamp": _now_iso(),
                "libro_slug": libro_slug,
                "libro": libro_nombre,
                "errores_analizados": len(session_errors),
                "mejoras_aplicadas": nuevas,
            }
        )
        _save_json(MEJORAS_LOG, data)
        return nuevas

    def _append_to_log(self, path: Path, entry: dict) -> None:
        log = _load_json(path, [])
        log.append(entry)
        _save_json(path, log)

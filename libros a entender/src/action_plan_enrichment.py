"""Enriquecimiento del plan de acción: escenarios, KPIs, concepto del libro y ejemplos oro."""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.rol_usuario import RolProfile

_META_ROOT = Path(__file__).resolve().parent.parent / "meta"
_EJEMPLOS_ORO_PATH = _META_ROOT / "plan_accion_ejemplos_oro.json"

ESCENARIOS_BY_FAMILIA: dict[str, list[str]] = {
    "psicopedagoga_educador": [
        "gabinete psicopedagógico",
        "aula",
        "familia",
        "equipo docente",
        "registro de seguimiento",
    ],
    "ingeniero_tecnico": [
        "taller o planta",
        "revisión de proceso",
        "equipo de obra",
        "cliente interno",
        "registro de incidencias",
    ],
    "emprendedor_negocio": [
        "operación diaria",
        "reunión con clientes",
        "equipo comercial",
        "finanzas",
        "registro semanal",
    ],
    "default": [
        "espacio de trabajo principal",
        "reunión de equipo",
        "cliente o usuario clave",
        "proceso crítico",
        "registro semanal",
    ],
}

REVISION_HUMANA_CHECKLIST = [
    "¿Suena a trabajo real del rol (gabinete, aula, familia)?",
    "¿El KPI se puede anotar el viernes con un número o escala?",
    "¿La acción está ligada a la idea del capítulo?",
    "¿Los verbos de apertura varían entre semanas?",
    "¿Venderías esta tabla a una colega del mismo oficio?",
]


def escenarios_para_rol(familia_rol: str) -> list[str]:
    return ESCENARIOS_BY_FAMILIA.get(familia_rol) or ESCENARIOS_BY_FAMILIA["default"]


def rotar_kpis(kpis: list[str], n: int) -> list[str]:
    if not kpis:
        return [""] * n
    assigned = [kpis[i % len(kpis)] for i in range(n)]
    for i in range(2, len(assigned)):
        if assigned[i] == assigned[i - 1] == assigned[i - 2]:
            for j in range(1, len(kpis) + 1):
                alt = kpis[(i + j) % len(kpis)]
                if alt != assigned[i]:
                    assigned[i] = alt
                    break
    return assigned


def resumir_concepto(idea_clave: str, *, max_len: int = 52) -> str:
    t = re.sub(r"\d+\s*%?", "", idea_clave or "")
    t = re.sub(r"\s+", " ", t).strip()
    sent = re.split(r"[.!?]", t)[0].strip()
    if len(sent) > max_len:
        sent = sent[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return sent


def load_ejemplos_oro(familia_rol: str) -> list[dict[str, str]]:
    try:
        data = json.loads(_EJEMPLOS_ORO_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = data.get(familia_rol) or data.get("default") or []
    return [r for r in rows if isinstance(r, dict)]


def format_ejemplos_oro_block(ejemplos: list[dict[str, str]]) -> str:
    if not ejemplos:
        return ""
    lines = ["EJEMPLOS ORO (copia este nivel de calidad):"]
    for i, ex in enumerate(ejemplos[:3], 1):
        lines.append(
            f"{i}. «{ex.get('concepto_libro', '')}» · {ex.get('escenario', '')} · "
            f"{ex.get('accion_concreta', '')}"
        )
    return "\n".join(lines)


def enrich_temas_payload(
    payload: list[dict[str, str]],
    profile: RolProfile | None,
) -> list[dict[str, str]]:
    familia = (profile.familia_rol if profile else "") or "default"
    escenarios = escenarios_para_rol(familia)
    kpis = list(profile.kpis) if profile and profile.kpis else []
    kpi_asignados = rotar_kpis(kpis, len(payload))

    enriched: list[dict[str, str]] = []
    for i, item in enumerate(payload):
        row = dict(item)
        row["escenario"] = escenarios[i % len(escenarios)]
        row["kpi_asignado"] = kpi_asignados[i] if i < len(kpi_asignados) else ""
        row["concepto_libro"] = resumir_concepto(row.get("idea_clave", ""))
        enriched.append(row)
    return enriched


def merge_row_metadata(
    filas: list,
    payload: list[dict[str, str]],
) -> list:
    """Copia concepto_libro, escenario y kpi_asignado del payload enriquecido."""
    from src.action_plan import ActionPlanRow

    by_tema = {p["tema"]: p for p in payload}
    out: list[ActionPlanRow] = []
    for row in filas:
        meta = by_tema.get(row.tema, {})
        out.append(
            ActionPlanRow(
                numero=row.numero,
                tema=row.tema,
                accion_concreta=row.accion_concreta,
                concepto_libro=str(meta.get("concepto_libro") or getattr(row, "concepto_libro", "") or ""),
                escenario=str(meta.get("escenario") or getattr(row, "escenario", "") or ""),
                kpi_asignado=str(meta.get("kpi_asignado") or getattr(row, "kpi_asignado", "") or ""),
            )
        )
    return out


def semanas_context(payload: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "tema": p["tema"],
            "idea_clave": p.get("idea_clave", ""),
            "concepto_libro": p.get("concepto_libro", ""),
            "escenario": p.get("escenario", ""),
            "kpi_asignado": p.get("kpi_asignado", ""),
        }
        for p in payload
    ]

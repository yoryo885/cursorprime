"""Sub-agentes con cargos especializados para el plan de acción semanal."""
from __future__ import annotations

import json
import re
from typing import Any

from src.action_plan import ActionPlanRow, Vital20Labels
from src.action_plan_validation import EJEMPLOS_KPI_MEDIBLE, FORMATO_ACCION
from src.action_plan_enrichment import format_ejemplos_oro_block, load_ejemplos_oro

ENFOQUES_SEMANALES = (
    "Semana de auditoría: mapea dónde se concentra el impacto real",
    "Semana de registro: mide tiempo, intervenciones y resultados observables",
    "Semana de triaje: separa urgente de importante en tu carga",
    "Semana de priorización: elige qué casos mueven KPIs esta quincena",
    "Semana de foco: elimina una fuente de dispersión concreta",
    "Semana de tiempo: redistribuye horas según impacto medido",
    "Semana de eficacia: conserva solo lo que produce avance documentable",
    "Semana de poda: deja de hacer una tarea de bajo impacto",
    "Semana de decisión: define criterios escritos para nuevos casos",
    "Semana de hábito: convierte el aprendizaje en rutina mínima sostenible",
)


class ActionPlanEncabezadosSubAgent:
    """Cargo: Estratega de encabezados."""

    CARGO = "Estratega de encabezados"

    def run(
        self,
        llm,
        *,
        libro_nombre: str,
        rol_block: str,
        num_temas: int,
    ) -> dict[str, str]:
        prompt = f"""Eres el ESTRATEGA DE ENCABEZADOS de un plan de acción semanal.

Libro: «{libro_nombre}» · {num_temas} semanas

{rol_block}

Responde SOLO JSON:
{{
  "titulo_plan": "PLAN DE ACCIÓN · [concepto del libro, MAYÚSCULAS]",
  "instruccion": "Una frase sobre marcar al completar de verdad (adaptada al oficio)",
  "cita": "Frase 20/80 en lenguaje del rol",
  "vital_col1": "Encabezado columna 1",
  "vital_col2": "Qué dejar de hacer",
  "vital_col3": "Lo aprendido",
  "vital_col4": "Lo que cambiarás"
}}"""

        raw = llm.call(prompt)
        data = _parse_json(raw) or {}
        return {
            "titulo_plan": str(data.get("titulo_plan") or "PLAN DE ACCIÓN"),
            "instruccion": str(
                data.get("instruccion")
                or "Una acción por semana. Márcala al completar. Reutiliza la plantilla en otras tareas."
            ),
            "cita": str(
                data.get("cita")
                or "El 20% de lo que haces genera el 80% de lo que consigues."
            ),
            "vital_col1": str(data.get("vital_col1") or Vital20Labels.col1),
            "vital_col2": str(data.get("vital_col2") or Vital20Labels.col2),
            "vital_col3": str(data.get("vital_col3") or Vital20Labels.col3),
            "vital_col4": str(data.get("vital_col4") or Vital20Labels.col4),
        }


class ActionPlanRedactorSubAgent:
    """Cargo: Redactor de acciones."""

    CARGO = "Redactor de acciones"

    def run(
        self,
        llm,
        *,
        libro_nombre: str,
        temas_payload: list[dict[str, str]],
        rol_block: str,
        familia_rol: str = "",
    ) -> list[ActionPlanRow]:
        for i, tp in enumerate(temas_payload):
            tp["enfoque_semana"] = ENFOQUES_SEMANALES[i % len(ENFOQUES_SEMANALES)]
            tp["numero_semana"] = i + 1

        ejemplos_block = format_ejemplos_oro_block(load_ejemplos_oro(familia_rol))

        prompt = f"""Eres el REDACTOR DE ACCIONES de un plan semanal profesional.

Libro: «{libro_nombre}»

{rol_block}

{FORMATO_ACCION}

{ejemplos_block}

REGLAS OBLIGATORIAS (cada fila):
- concepto_libro del payload → reflejar en el primer paso (idea del capítulo)
- escenario del payload → nombrar en el primer paso (gabinete, aula, familia…)
- kpi_asignado del payload → usar en el último paso (Registra:/Mide: + unidad)
- Ritual reutilizable · imperativo en «tú» · sin cifras inventadas
- Verbo inicial distinto en cada semana (audita, observa, prioriza, coordina…)
- Ejemplos KPI: {EJEMPLOS_KPI_MEDIBLE}

Temas (usa escenario, concepto_libro y kpi_asignado de cada uno):
{json.dumps(temas_payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON:
{{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}
Exactamente {len(temas_payload)} filas."""

        return _filas_desde_json(llm.call(prompt), temas_payload)


class ActionPlanEditorSubAgent:
    """Cargo: Editor de integridad."""

    CARGO = "Editor de integridad"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas_a_corregir: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_a_corregir:
            return filas

        payload = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema in temas_a_corregir
        ]
        prompt = f"""Eres el EDITOR DE INTEGRIDAD del plan de acción.

{rol_block}

Completa acciones rotas. {FORMATO_ACCION} Sin cifras inventadas.

{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanDiversidadSubAgent:
    """Cargo: Curador de diversidad."""

    CARGO = "Curador de diversidad"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas_repetidos: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_repetidos:
            return filas

        repetidas = [f for f in filas if f.tema in temas_repetidos]
        contexto = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema not in temas_repetidos
        ][:4]

        prompt = f"""Eres el CURADOR DE DIVERSIDAD del plan de acción.

{rol_block}

Reescribe con enfoques distintos. {FORMATO_ACCION}

Estilo ya usado (no repetir):
{json.dumps(contexto, ensure_ascii=False, indent=2)}

Reescribir:
{json.dumps([{"tema": f.tema, "accion_concreta": f.accion_concreta} for f in repetidas], ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanRolGuardSubAgent:
    """Cargo: Guardián de rol."""

    CARGO = "Guardián de rol"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas_problema: list[str],
        prohibido: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_problema:
            return filas

        payload = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema in temas_problema
        ]
        prompt = f"""Eres el GUARDIÁN DE ROL del plan de acción.

{rol_block}

Prohibido: {", ".join(prohibido[:12])}

Reescribe solo tareas del ROL. {FORMATO_ACCION}

{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanKPIAncladorSubAgent:
    """Cargo: Anclador de KPIs."""

    CARGO = "Anclador de KPIs"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        kpis: list[str],
        temas_sin_kpi: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_sin_kpi or not kpis:
            return filas

        payload = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema in temas_sin_kpi
        ]
        prompt = f"""Eres el ANCLADOR DE KPIs.

{rol_block}

KPIs del rol: {", ".join(kpis)}

El último paso DEBE ser medible: Registra:/Mide: + unidad contable u observable.
Ejemplos: {EJEMPLOS_KPI_MEDIBLE}
Prohibido: frases vagas («objetivos cumplidos», «avance verificable»).

{FORMATO_ACCION}

{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanAnclajeSubAgent:
    """Cargo: Anclador de libro — concepto del capítulo + escenario + KPI asignado."""

    CARGO = "Anclador de libro"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas_payload: list[dict[str, str]],
        temas_problema: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_problema:
            return filas

        by_tema = {p["tema"]: p for p in temas_payload}
        payload = []
        for f in filas:
            if f.tema not in temas_problema:
                continue
            meta = by_tema.get(f.tema, {})
            payload.append(
                {
                    "tema": f.tema,
                    "accion_concreta": f.accion_concreta,
                    "concepto_libro": meta.get("concepto_libro", ""),
                    "escenario": meta.get("escenario", ""),
                    "kpi_asignado": meta.get("kpi_asignado", ""),
                }
            )

        prompt = f"""Eres el ANCLADOR DE LIBRO del plan de acción.

{rol_block}

{FORMATO_ACCION}

Reescribe cada acción anclándola al libro:
1. Primer paso: escenario + idea del concepto_libro
2. Último paso: kpi_asignado medible (Registra:/Mide: + cuántos/minutos/escala)
3. Verbo inicial distinto al resto del plan

Filas:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanCifrasGuardSubAgent:
    """Cargo: Validador de cifras — elimina números y suposiciones inventadas."""

    CARGO = "Validador de cifras"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas_problema: list[str],
    ) -> list[ActionPlanRow]:
        if not temas_problema:
            return filas

        payload = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema in temas_problema
        ]
        prompt = f"""Eres el VALIDADOR DE CIFRAS del plan de acción.

{rol_block}

{FORMATO_ACCION}

Elimina TODAS las cifras concretas y «supongamos». Usa: tu carga, tus casos, tus casos críticos, esta semana.

{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


class ActionPlanPracticaSubAgent:
    """Cargo: Sintetizador práctico — acciones cortas, reutilizables, estilo checklist."""

    CARGO = "Sintetizador práctico"

    def run(
        self,
        llm,
        filas: list[ActionPlanRow],
        *,
        rol_block: str,
        temas: list[str] | None = None,
    ) -> list[ActionPlanRow]:
        targets = temas or [f.tema for f in filas]
        payload = [
            {"tema": f.tema, "accion_concreta": f.accion_concreta}
            for f in filas
            if f.tema in targets
        ]
        if not payload:
            return filas

        prompt = f"""Eres el SINTETIZADOR PRÁCTICO del plan de acción.

{rol_block}

{FORMATO_ACCION}

Convierte cada acción en una PLANTILLA REUTILIZABLE:
- 2-3 pasos máximo, separados por « · »
- Cada paso ≤ 8 palabras, imperativo en «tú»
- Último paso MEDIBLE: «Registra: cuántas [KPI]» o «Mide: minutos por caso crítico»
- Ejemplos: {EJEMPLOS_KPI_MEDIBLE}
- Sin párrafos · sin cifras · usable cada semana en otra tarea

Acciones:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Responde SOLO JSON: {{"filas": [{{"tema": "...", "accion_concreta": "..."}}]}}"""

        return _merge_filas(filas, llm.call(prompt))


def _parse_json(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _merge_filas(filas: list[ActionPlanRow], raw: str) -> list[ActionPlanRow]:
    data = _parse_json(raw) or {}
    corregidas = {
        str(x.get("tema")): str(x.get("accion_concreta", "")).strip()
        for x in data.get("filas", [])
    }
    out: list[ActionPlanRow] = []
    for row in filas:
        if row.tema in corregidas and corregidas[row.tema]:
            out.append(
                ActionPlanRow(
                    row.numero,
                    row.tema,
                    corregidas[row.tema],
                    concepto_libro=row.concepto_libro,
                    escenario=row.escenario,
                    kpi_asignado=row.kpi_asignado,
                )
            )
        else:
            out.append(row)
    return out


def _filas_desde_json(raw: str, temas_payload: list[dict[str, str]]) -> list[ActionPlanRow]:
    data = _parse_json(raw) or {}
    filas_raw = data.get("filas") or []
    rows: list[ActionPlanRow] = []

    for i, item in enumerate(filas_raw):
        tema = str(item.get("tema", "") or "").strip()
        accion = str(item.get("accion_concreta", "") or "").strip()
        if not tema and i < len(temas_payload):
            tema = temas_payload[i].get("tema", "")
        if tema and accion:
            meta = temas_payload[i] if i < len(temas_payload) else {}
            rows.append(
                ActionPlanRow(
                    numero=f"{i + 1:02d}",
                    tema=tema,
                    accion_concreta=accion,
                    concepto_libro=str(meta.get("concepto_libro", "")),
                    escenario=str(meta.get("escenario", "")),
                    kpi_asignado=str(meta.get("kpi_asignado", "")),
                )
            )

    if len(rows) < len(temas_payload):
        rows_by_tema = {r.tema: r for r in rows}
        rebuilt: list[ActionPlanRow] = []
        for i, tp in enumerate(temas_payload):
            tema = tp["tema"]
            if tema in rows_by_tema:
                row = rows_by_tema[tema]
            else:
                esc = tp.get("escenario", "tu espacio de trabajo")
                kpi = tp.get("kpi_asignado", "resultado medible")
                row = ActionPlanRow(
                    numero=f"{i + 1:02d}",
                    tema=tema,
                    accion_concreta=(
                        f"En {esc} revisa casos críticos · Prioriza por impacto · "
                        f"Registra: cuántas {kpi} esta semana"
                    ),
                    concepto_libro=str(tp.get("concepto_libro", "")),
                    escenario=str(tp.get("escenario", "")),
                    kpi_asignado=str(tp.get("kpi_asignado", "")),
                )
            row.numero = f"{i + 1:02d}"
            if not row.concepto_libro:
                row.concepto_libro = str(tp.get("concepto_libro", ""))
            if not row.escenario:
                row.escenario = str(tp.get("escenario", ""))
            if not row.kpi_asignado:
                row.kpi_asignado = str(tp.get("kpi_asignado", ""))
            rebuilt.append(row)
        rows = rebuilt

    return rows[: len(temas_payload)]

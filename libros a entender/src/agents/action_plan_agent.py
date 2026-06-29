"""Orquestador del plan de acción con cargos especializados."""
from __future__ import annotations

import json
from pathlib import Path

from src.action_plan import (
    ActionPlan,
    ActionPlanRow,
    Vital20Labels,
    load_action_plan,
    save_action_plan,
)
from src.action_plan_enrichment import (
    REVISION_HUMANA_CHECKLIST,
    enrich_temas_payload,
    merge_row_metadata,
    semanas_context,
)
from src.action_plan_validation import (
    accion_muy_larga,
    accion_truncada,
    concepto_anclado,
    escenario_presente,
    filas_repetitivas,
    formato_practico_ok,
    kpi_asignado_ok,
    kpi_medible_ok,
    kpi_presente,
    tiene_cifras_inventadas,
    terminos_fuera_rol,
    validate_action_plan,
    verbos_apertura_repetidos,
)
from src.agents.action_plan_subagents import (
    ActionPlanAnclajeSubAgent,
    ActionPlanCifrasGuardSubAgent,
    ActionPlanDiversidadSubAgent,
    ActionPlanEditorSubAgent,
    ActionPlanEncabezadosSubAgent,
    ActionPlanKPIAncladorSubAgent,
    ActionPlanPracticaSubAgent,
    ActionPlanRedactorSubAgent,
    ActionPlanRolGuardSubAgent,
)
from src.config import VOZ_NOMBRE
from src.models import TopicResult
from src.output_paths import meta_dir
from src.rol_usuario import build_rol_block, ensure_rol_perfil

MAX_REFINE_ROUNDS = 3
QC_REPORT_FILENAME = "plan_accion_qc.json"


class ActionPlanAgent:
    """Coordina redacción, edición, diversidad, rol, KPIs y QC del plan semanal."""

    def __init__(self, llm):
        self.llm = llm
        self._encabezados = ActionPlanEncabezadosSubAgent()
        self._redactor = ActionPlanRedactorSubAgent()
        self._editor = ActionPlanEditorSubAgent()
        self._diversidad = ActionPlanDiversidadSubAgent()
        self._rol_guard = ActionPlanRolGuardSubAgent()
        self._kpi = ActionPlanKPIAncladorSubAgent()
        self._cifras = ActionPlanCifrasGuardSubAgent()
        self._practica = ActionPlanPracticaSubAgent()
        self._anclaje = ActionPlanAnclajeSubAgent()

    def run(
        self,
        resultados: list[TopicResult],
        tablas: list,
        *,
        libro_nombre: str,
        output_dir,
        force: bool = False,
    ) -> ActionPlan | None:
        output_dir = Path(output_dir)
        if not force:
            existing = load_action_plan(output_dir)
            if existing and existing.filas:
                print(f"   ⏭️  Plan de acción: reutilizando {len(existing.filas)} filas")
                return existing

        temas_ok = [r for r in resultados if not r.fallo and r.tema]
        if not temas_ok:
            print("   ⏭️  Plan de acción: sin temas")
            return None
        if not self.llm:
            return load_action_plan(output_dir)

        print(f"   📋 Plan de acción: pipeline con cargos ({len(temas_ok)} semanas)...")
        profile = ensure_rol_perfil(output_dir, llm=self.llm)
        rol_block = build_rol_block(profile, agent="aplicacion")
        kpis = list(profile.kpis) if profile else []
        prohibido = list(profile.prohibido) if profile else []

        temas_payload = enrich_temas_payload(
            self._build_payload(temas_ok, tablas),
            profile,
        )
        semanas_ctx = semanas_context(temas_payload)
        familia_rol = profile.familia_rol if profile else "default"

        print(f"      → Cargo: {self._encabezados.CARGO}")
        meta = self._encabezados.run(
            self.llm,
            libro_nombre=libro_nombre,
            rol_block=rol_block,
            num_temas=len(temas_ok),
        )

        print(f"      → Cargo: {self._redactor.CARGO}")
        filas = self._redactor.run(
            self.llm,
            libro_nombre=libro_nombre,
            temas_payload=temas_payload,
            rol_block=rol_block,
            familia_rol=familia_rol,
        )
        filas = merge_row_metadata(filas, temas_payload)

        for round_idx in range(1, MAX_REFINE_ROUNDS + 1):
            truncadas = [f.tema for f in filas if accion_truncada(f.accion_concreta)]
            largas = [f.tema for f in filas if accion_muy_larga(f.accion_concreta)]
            mal_formato = [f.tema for f in filas if not formato_practico_ok(f.accion_concreta)]
            con_cifras = [f.tema for f in filas if tiene_cifras_inventadas(f.accion_concreta)]

            if con_cifras:
                print(f"      → Cargo: {self._cifras.CARGO} ({len(con_cifras)})")
                filas = self._cifras.run(
                    self.llm, filas, rol_block=rol_block, temas_problema=con_cifras
                )

            if truncadas:
                print(f"      → Cargo: {self._editor.CARGO} ({len(truncadas)})")
                filas = self._editor.run(
                    self.llm, filas, rol_block=rol_block, temas_a_corregir=truncadas
                )

            if largas or mal_formato or round_idx == MAX_REFINE_ROUNDS:
                temas_practica = list(dict.fromkeys(largas + mal_formato + [f.tema for f in filas]))
                print(f"      → Cargo: {self._practica.CARGO} ({len(temas_practica)} filas)")
                filas = self._practica.run(
                    self.llm, filas, rol_block=rol_block, temas=temas_practica
                )

            repetidas = filas_repetitivas(filas)
            if repetidas:
                print(f"      → Cargo: {self._diversidad.CARGO} ({len(repetidas)})")
                filas = self._diversidad.run(
                    self.llm,
                    filas,
                    rol_block=rol_block,
                    temas_repetidos=repetidas,
                )

            fuera_rol: list[str] = []
            for f in filas:
                if terminos_fuera_rol(f.accion_concreta, prohibido):
                    fuera_rol.append(f.tema)
            if fuera_rol:
                print(f"      → Cargo: {self._rol_guard.CARGO} ({len(fuera_rol)})")
                filas = self._rol_guard.run(
                    self.llm,
                    filas,
                    rol_block=rol_block,
                    temas_problema=fuera_rol,
                    prohibido=prohibido,
                )

            temas_anclaje = self._temas_fallos_anclaje(filas, semanas_ctx)
            if temas_anclaje:
                print(f"      → Cargo: {self._anclaje.CARGO} ({len(temas_anclaje)})")
                filas = self._anclaje.run(
                    self.llm,
                    filas,
                    rol_block=rol_block,
                    temas_payload=temas_payload,
                    temas_problema=temas_anclaje[:8],
                )
                filas = merge_row_metadata(filas, temas_payload)

            sin_kpi = [
                f.tema
                for f in filas
                if kpis
                and (
                    not kpi_presente(f.accion_concreta, kpis)
                    or not kpi_medible_ok(f.accion_concreta, kpis)
                    or not kpi_asignado_ok(f.accion_concreta, f.kpi_asignado)
                )
            ]
            if sin_kpi:
                print(f"      → Cargo: {self._kpi.CARGO} ({len(sin_kpi)})")
                filas = self._kpi.run(
                    self.llm,
                    filas,
                    rol_block=rol_block,
                    kpis=kpis,
                    temas_sin_kpi=sin_kpi[:8],
                )
                filas = merge_row_metadata(filas, temas_payload)

            qc = validate_action_plan(
                ActionPlan("", "", "", "", filas=filas),
                kpis=kpis,
                prohibido=prohibido,
                semanas_ctx=semanas_ctx,
            )
            if qc.passed:
                break

        plan = self._build_plan(meta, filas, libro_nombre)
        qc_final = validate_action_plan(
            plan, kpis=kpis, prohibido=prohibido, semanas_ctx=semanas_ctx
        )
        self._save_qc(output_dir, qc_final)

        save_action_plan(output_dir, plan)
        estado = "✅" if qc_final.passed else "⚠️ "
        print(
            f"      {estado} Plan guardado — QC: "
            f"{sum(1 for i in qc_final.issues if i.severity == 'error')} errores, "
            f"{sum(1 for i in qc_final.issues if i.severity == 'warning')} avisos"
        )
        return plan

    @staticmethod
    def _build_payload(temas_ok: list[TopicResult], tablas: list) -> list[dict[str, str]]:
        tablas_map = {t.tema: t for t in tablas}
        payload = []
        for r in temas_ok:
            t = tablas_map.get(r.tema)
            payload.append(
                {
                    "tema": r.tema,
                    "idea_clave": getattr(t, "idea_clave", "") if t else "",
                    "aplicacion": getattr(t, "aplicacion_vida_real", "") if t else "",
                    "resumen_breve": (r.resumen_voz or r.resumen)[:400],
                }
            )
        return payload

    @staticmethod
    def _build_plan(meta: dict[str, str], filas: list[ActionPlanRow], libro_nombre: str) -> ActionPlan:
        titulo_libro, autor = _split_libro(libro_nombre)
        libro_line = (
            f"{titulo_libro} · {autor} · Por {VOZ_NOMBRE}"
            if autor
            else f"{titulo_libro} · Por {VOZ_NOMBRE}"
        )
        footer = (
            f"{titulo_libro} · {autor} · Resumen y Plan de Acción por {VOZ_NOMBRE}"
            if autor
            else f"{titulo_libro} · Resumen y Plan de Acción por {VOZ_NOMBRE}"
        )
        return ActionPlan(
            titulo_plan=meta["titulo_plan"],
            libro_line=libro_line,
            instruccion=meta["instruccion"],
            cita=meta["cita"],
            filas=filas,
            vital_20=Vital20Labels(
                col1=meta["vital_col1"],
                col2=meta["vital_col2"],
                col3=meta["vital_col3"],
                col4=meta["vital_col4"],
            ),
            footer=footer,
        )

    @staticmethod
    def _temas_fallos_anclaje(
        filas: list[ActionPlanRow],
        semanas_ctx: list[dict],
    ) -> list[str]:
        ctx_map = {c["tema"]: c for c in semanas_ctx}
        verbos_rep = set(verbos_apertura_repetidos(filas))
        fallos: list[str] = []
        for row in filas:
            ctx = ctx_map.get(row.tema, {})
            escenario = row.escenario or ctx.get("escenario", "")
            idea = ctx.get("idea_clave", "")
            concepto = row.concepto_libro or ctx.get("concepto_libro", "")
            if escenario and not escenario_presente(row.accion_concreta, escenario):
                fallos.append(row.tema)
            elif (idea or concepto) and not concepto_anclado(
                row.accion_concreta, idea, concepto
            ):
                fallos.append(row.tema)
            elif row.kpi_asignado and not kpi_asignado_ok(
                row.accion_concreta, row.kpi_asignado
            ):
                fallos.append(row.tema)
            elif row.tema in verbos_rep:
                fallos.append(row.tema)
        return list(dict.fromkeys(fallos))

    @staticmethod
    def _save_qc(output_dir: Path, qc) -> None:
        path = meta_dir(output_dir) / QC_REPORT_FILENAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "passed": qc.passed,
                    "issues": [
                        {
                            "severity": i.severity,
                            "cargo": i.cargo,
                            "tema": i.tema,
                            "message": i.message,
                        }
                        for i in qc.issues
                    ],
                    "revision_humana": [
                        {"item": item, "checked": False}
                        for item in REVISION_HUMANA_CHECKLIST
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


def _split_libro(libro_nombre: str) -> tuple[str, str]:
    if " - " in libro_nombre:
        a, b = libro_nombre.split(" - ", 1)
        return a.strip(), b.strip()
    return libro_nombre.strip(), ""

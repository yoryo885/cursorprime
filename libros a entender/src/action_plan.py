"""Modelo y persistencia del plan de acción (última página del PDF)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.output_paths import meta_dir

PLAN_ACCION_FILENAME = "plan_accion.json"

AVISO_MATERIAL_APOYO = (
    "Material de apoyo · No sustituye criterio profesional ni protocolo clínico."
)


@dataclass
class ActionPlanRow:
    numero: str
    tema: str
    accion_concreta: str
    concepto_libro: str = ""
    escenario: str = ""
    kpi_asignado: str = ""


@dataclass
class Vital20Labels:
    col1: str = "MIS 3 PRIORIDADES QUE MÁS IMPACTAN"
    col2: str = "LO QUE VOY A DEJAR DE HACER"
    col3: str = "LO QUE APRENDÍ"
    col4: str = "LO QUE VOY A CAMBIAR"


@dataclass
class ActionPlan:
    titulo_plan: str
    libro_line: str
    instruccion: str
    cita: str
    filas: list[ActionPlanRow] = field(default_factory=list)
    vital_20: Vital20Labels = field(default_factory=Vital20Labels)
    footer: str = ""
    aviso_legal: str = AVISO_MATERIAL_APOYO
    incluir_plantilla_vacia: bool = True
    titulo_plantilla_vacia: str = "TU PLAN DE ACCIÓN · A COMPLETAR"
    instruccion_plantilla_vacia: str = (
        "Usa esta hoja para escribir tus propias acciones semanales, "
        "adaptadas a tu gabinete y a tu carga real."
    )

    def to_dict(self) -> dict:
        return {
            "titulo_plan": self.titulo_plan,
            "libro_line": self.libro_line,
            "instruccion": self.instruccion,
            "cita": self.cita,
            "filas": [asdict(f) for f in self.filas],
            "vital_20": asdict(self.vital_20),
            "footer": self.footer,
            "aviso_legal": self.aviso_legal,
            "incluir_plantilla_vacia": self.incluir_plantilla_vacia,
            "titulo_plantilla_vacia": self.titulo_plantilla_vacia,
            "instruccion_plantilla_vacia": self.instruccion_plantilla_vacia,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ActionPlan:
        vital = data.get("vital_20") or {}
        filas = [
            ActionPlanRow(
                numero=str(f.get("numero", "")),
                tema=str(f.get("tema", "")),
                accion_concreta=str(f.get("accion_concreta", "")),
                concepto_libro=str(f.get("concepto_libro", "") or ""),
                escenario=str(f.get("escenario", "") or ""),
                kpi_asignado=str(f.get("kpi_asignado", "") or ""),
            )
            for f in data.get("filas", [])
            if f.get("tema")
        ]
        return cls(
            titulo_plan=str(data.get("titulo_plan", "")),
            libro_line=str(data.get("libro_line", "")),
            instruccion=str(data.get("instruccion", "")),
            cita=str(data.get("cita", "")),
            filas=filas,
            vital_20=Vital20Labels(
                col1=str(vital.get("col1", Vital20Labels.col1)),
                col2=str(vital.get("col2", Vital20Labels.col2)),
                col3=str(vital.get("col3", Vital20Labels.col3)),
                col4=str(vital.get("col4", Vital20Labels.col4)),
            ),
            footer=str(data.get("footer", "")),
            aviso_legal=str(data.get("aviso_legal") or AVISO_MATERIAL_APOYO),
            incluir_plantilla_vacia=bool(data.get("incluir_plantilla_vacia", True)),
            titulo_plantilla_vacia=str(
                data.get("titulo_plantilla_vacia") or "TU PLAN DE ACCIÓN · A COMPLETAR"
            ),
            instruccion_plantilla_vacia=str(
                data.get("instruccion_plantilla_vacia")
                or (
                    "Usa esta hoja para escribir tus propias acciones semanales, "
                    "adaptadas a tu gabinete y a tu carga real."
                )
            ),
        )


def action_plan_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / PLAN_ACCION_FILENAME


def load_action_plan(output_dir: Path) -> ActionPlan | None:
    path = action_plan_path(output_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        plan = ActionPlan.from_dict(data)
        return plan if plan.filas else None
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def save_action_plan(output_dir: Path, plan: ActionPlan) -> Path:
    path = action_plan_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path

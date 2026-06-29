"""Agente 3: diseña plan.json del proyecto destino."""

from __future__ import annotations

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class ArchitectureAgent:
    DEFAULT_STEPS = [
        {
            "id": 1,
            "slug": "context",
            "nombre": "Cargar contexto",
            "agente": "ContextAgent",
            "required": True,
            "flag_cli": "--solo-context",
            "input": ["data/{slug}/inputs/"],
            "output": ["data/{slug}/meta/context.json"],
        },
        {
            "id": 2,
            "slug": "collect",
            "nombre": "Recolectar datos proveedor",
            "agente": "CollectorAgent",
            "required": True,
            "flag_cli": "--solo-collect",
            "input": ["data/{slug}/meta/context.json"],
            "output": ["data/{slug}/meta/catalog.json"],
        },
        {
            "id": 3,
            "slug": "margin",
            "nombre": "Calcular márgenes",
            "agente": "MarginAgent",
            "required": True,
            "flag_cli": "--solo-margin",
            "input": ["data/{slug}/meta/catalog.json"],
            "output": ["data/{slug}/meta/margins.json"],
        },
        {
            "id": 4,
            "slug": "report",
            "nombre": "Generar reporte",
            "agente": "ReportAgent",
            "required": True,
            "flag_cli": "--solo-report",
            "input": ["data/{slug}/meta/margins.json"],
            "output": ["data/{slug}/output/report.json"],
        },
        {
            "id": 5,
            "slug": "qc",
            "nombre": "QC final",
            "agente": "QCAgent",
            "required": True,
            "flag_cli": "--solo-qc",
            "input": ["data/{slug}/output/report.json"],
            "output": ["data/{slug}/meta/qc_report.json"],
        },
    ]

    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = load_json(ctx.borrador_dir / "meta" / "brief.json", {})
        slug = ctx.slug

        plan = {
            "version": 1,
            "proyecto": brief.get("nombre", slug),
            "slug": slug,
            "descripcion": brief.get("modelo_negocio") or brief.get("problema", ""),
            "pipeline": self.DEFAULT_STEPS,
            "defaults": {
                "checkpoint": True,
                "mock_external": True,
            },
        }

        out = ctx.borrador_dir / "meta" / "plan.json"
        save_json(out, plan)
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"Plan destino con {len(self.DEFAULT_STEPS)} pasos")

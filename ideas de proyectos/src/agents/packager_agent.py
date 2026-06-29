"""Agente 6: ENTREGA.txt y plan_accion.json."""

from __future__ import annotations

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class SpecPackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        if not ctx.autorizado_construir:
            raise PermissionError("Construcción bloqueada.")

        brief = load_json(ctx.borrador_dir / "meta" / "brief.json", {})
        feasibility = load_json(ctx.borrador_dir / "meta" / "feasibility.json", {})
        slug = ctx.slug
        root = ctx.proyecto_dir

        plan_accion = {
            "slug": slug,
            "mvp": feasibility.get("mvp", []),
            "v1": feasibility.get("v1", []),
            "futuro": feasibility.get("futuro", []),
            "checklist": [
                {"tarea": "Implementar CollectorAgent", "prioridad": 1},
                {"tarea": "Implementar MarginAgent con API ML", "prioridad": 2},
                {"tarea": "ReportAgent JSON + TXT", "prioridad": 3},
            ],
        }
        accion_path = root / "meta" / "plan_accion.json"
        save_json(accion_path, plan_accion)

        entrega = "\n".join(
            [
                f"PROYECTO: {brief.get('nombre', slug)}",
                f"SLUG: {slug}",
                f"VEREDICTO: {feasibility.get('veredicto', 'N/A')}",
                f"COMANDO: python {slug}_main.py --help",
                f"BORRADOR: borradores/{slug}/",
                "",
                "MVP PENDIENTE:",
                *[f"  - {x}" for x in feasibility.get("mvp", [])],
            ]
        )
        entrega_path = root / "ENTREGA.txt"
        entrega_path.write_text(entrega, encoding="utf-8")

        return AgentResult(
            ok=True,
            artifacts=[str(entrega_path), str(accion_path)],
            notes="Entrega empaquetada",
        )

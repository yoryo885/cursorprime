"""Planner: elige agentes/skills según receta y necesidad del video."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import save_json
from src.recipes import resolve_recipe, validate_requirements
from src.types import AgentResult, PipelineContext


class PlannerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        receta_cli = getattr(ctx, "receta", None)
        plan = resolve_recipe(ctx.lote, receta_cli)
        warnings = validate_requirements(plan, ctx.lote)

        # Aplicar plan al contexto en memoria
        ctx.salidas = list(plan["salidas"])
        ctx.lote = {
            **ctx.lote,
            "receta": plan["receta"],
            "salidas": plan["salidas"],
            "video": plan["video"],
            "copy": plan["copy"],
        }

        payload = {
            **plan,
            "slug": ctx.slug,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "warnings": warnings,
        }
        out = ctx.paths["plan_runtime"]
        save_json(out, payload)

        # Refrescar context.json con receta/salidas/video del plan
        from src.config import load_json

        context = load_json(ctx.paths["context"], {}) or {}
        context["receta"] = plan["receta"]
        context["salidas_pedidas"] = plan["salidas"]
        context["salidas_efectivas"] = plan["salidas"]
        context["video"] = plan["video"]
        context["copy"] = plan["copy"]
        context["skills_activadas"] = plan["skills"]
        context["agentes_plan"] = plan["agentes"]
        save_json(ctx.paths["context"], context)

        notes = f"Receta «{plan['receta']}» → {len(plan['agentes'])} agentes · skills: {', '.join(plan['skills']) or '—'}"
        return AgentResult(
            ok=True,
            artifacts=[str(out)],
            notes=notes,
            warnings=warnings,
        )

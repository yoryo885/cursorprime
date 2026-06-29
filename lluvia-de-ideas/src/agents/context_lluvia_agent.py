"""Agente: contexto para lluvia — lee análisis + dirección."""

from __future__ import annotations

from src.config import direccion_path, load_json, save_json
from src.types import AgentResult, PipelineContext


class ContextLluviaAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        analisis = load_json(ctx.paths["analisis"], {}) or {}
        direccion = load_json(direccion_path(), {})
        brief = ctx.brief or load_json(ctx.paths.get("brief", ctx.paths["meta"] / "brief.json"), {}) or {}

        context = {
            "slug": ctx.slug,
            "analisis_slug": brief.get("analisis_slug") or ctx.brief.get("analisis_slug"),
            "tema": analisis.get("tema") or brief.get("tema") or "cursorprime",
            "direccion": direccion.get("direccion") or [],
            "proyectos_activos": direccion.get("proyectos_activos") or [],
            "prioridades": direccion.get("prioridades") or [],
            "analisis_resumen": analisis.get("resumen_ejecutivo") or "",
            "oportunidades": analisis.get("oportunidades_pipeline") or [],
        }
        save_json(ctx.paths["context"], context)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["context"])])

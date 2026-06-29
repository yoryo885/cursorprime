"""Agente: normaliza brief de investigación."""

from __future__ import annotations

from src.config import load_json, save_json, slugify
from src.types import AgentResult, PipelineContext


class ContextInvestigacionAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        raw = ctx.brief or load_json(ctx.paths["brief"], {}) or {}
        tema = str(raw.get("tema") or raw.get("titulo") or ctx.slug).strip()
        queries = raw.get("queries") or []
        if not queries:
            queries = [
                f"{tema} youtube",
                f"{tema} amazon kdp",
                f"{tema} tendencias 2026",
            ]

        context = {
            "slug": ctx.slug,
            "tema": tema,
            "queries": queries[:6],
            "fuentes_pedidas": raw.get("fuentes") or ["youtube", "web"],
            "notas": raw.get("notas") or "",
        }
        save_json(ctx.paths["context"], context)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["context"])], notes=tema)

"""Agente 1 — Context Loader."""

from __future__ import annotations

from src.agents.base import envelope, tipo_negocio
from src.config import save_json
from src.types import AgentResult, PipelineContext


class ContextAgent:
    key = "context"

    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = ctx.idea
        data = envelope(
            "ContextAgent",
            confidence=0.9,
            error_margin_pct=5,
            findings=[
                f"Título: {idea.get('titulo', ctx.slug)}",
                f"Mercado: {idea.get('mercado', 'CL')}",
                f"Tipo: {tipo_negocio(idea)}",
            ],
            extra={
                "slug": ctx.slug,
                "titulo": idea.get("titulo") or ctx.slug,
                "tipo_negocio": tipo_negocio(idea),
                "mercado": idea.get("mercado", "CL"),
                "modo_pipeline": ctx.modo,
                "mock_web": ctx.mock_web,
                "idea_normalizada": idea,
            },
        )
        save_json(ctx.paths["context"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["context"])])

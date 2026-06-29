"""Agente 3 — Market Research."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope
from src.types import AgentResult, PipelineContext
from src.web_backend import search_market


class MarketResearchAgent:
    key = "market"

    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = load_json(ctx.paths["context"], {}).get("idea_normalizada", ctx.idea)
        m = search_market(idea, mock=ctx.mock_web)
        conf = 0.4 if ctx.mock_web else 0.6
        warnings = ["TAM estimado — ±40% sin fuentes premium"] 
        if ctx.mock_web:
            warnings.append("mock web activo")
        data = envelope(
            "MarketResearchAgent",
            confidence=conf,
            error_margin_pct=40,
            metrics={
                "tam_usd": m["tam_usd"],
                "crecimiento_anual_pct": m["crecimiento_anual_pct"],
                "demanda_score": m["demanda_score"],
            },
            sources=m["sources"],
            warnings=warnings,
        )
        save_json(ctx.paths["market"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["market"])])

"""Agente 2 — Trend."""

from __future__ import annotations

from src.agents.base import envelope
from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext
from src.web_backend import search_trends


class TrendAgent:
    key = "trend"

    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = load_json(ctx.paths["context"], {}).get("idea_normalizada", ctx.idea)
        kws = idea.get("keywords") or [idea.get("titulo", "")]
        mercado = idea.get("mercado") or "CL"
        trends = search_trends(kws, mock=ctx.mock_web, mercado=mercado)

        is_mock = trends.get("mock", ctx.mock_web)
        conf = 0.45 if is_mock else 0.72
        warnings = list(trends.get("warnings") or [])
        if is_mock and ctx.mock_web:
            warnings.append("MOCK_WEB=true — usa --no-mock-web para Google Trends real")

        score = trends["trend_score"]
        findings = [
            f"Dirección: {trends['direccion']}",
            f"Interés promedio Google (0-100): {trends.get('interest_avg', '?')}",
            f"Geo: {trends.get('geo', mercado)}",
        ]

        data = envelope(
            "TrendAgent",
            confidence=conf,
            error_margin_pct=25 if not is_mock else 35,
            metrics={"trend_score": {"min": max(1, score - 1), "max": min(10, score + 1), "point": score}},
            findings=findings,
            sources=trends["sources"],
            warnings=warnings,
            extra={
                "direccion": trends["direccion"],
                "keywords": trends["keywords"],
                "interest_by_keyword": trends.get("interest_by_keyword", {}),
                "mock": is_mock,
            },
        )
        save_json(ctx.paths["trend"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["trend"])], warnings=warnings)
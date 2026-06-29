"""Agente 6 — Scalability."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope, metric, tipo_negocio
from src.types import AgentResult, PipelineContext


class ScalabilityAgent:
    key = "scalability"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        tipo = context.get("tipo_negocio") or tipo_negocio(ctx.idea)
        scores = {"saas": 8, "marketplace": 6, "ecommerce": 5, "servicio": 6}
        s = scores.get(tipo, 6)
        bottlenecks = []
        if tipo == "servicio":
            bottlenecks.append("Onboarding manual por cliente")
        if tipo == "ecommerce":
            bottlenecks.append("Stock/proveedor")
        data = envelope(
            "ScalabilityAgent",
            confidence=0.55,
            error_margin_pct=20,
            metrics={"scalability_score": metric(s - 2, s + 1, s)},
            findings=bottlenecks or ["Automatización parcial posible"],
            extra={"bottlenecks": bottlenecks},
        )
        save_json(ctx.paths["scalability"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["scalability"])])

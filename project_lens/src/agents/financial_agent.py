"""Agente 5 — Financial."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope, metric, tipo_negocio
from src.types import AgentResult, PipelineContext

MARGEN_POR_TIPO = {
    "saas": (55, 85, 70),
    "ecommerce": (8, 28, 15),
    "marketplace": (12, 30, 20),
    "servicio": (25, 55, 38),
}


class FinancialAgent:
    key = "financial"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        idea = context.get("idea_normalizada", ctx.idea)
        tipo = context.get("tipo_negocio") or tipo_negocio(idea)
        lo, hi, pt = MARGEN_POR_TIPO.get(tipo, (15, 45, 28))

        planes = idea.get("planes") or {}
        if planes:
            mensuales = [p.get("mensual_clp", 0) for p in planes.values() if isinstance(p, dict)]
            if mensuales:
                pt = max(lo, min(hi, sum(mensuales) / len(mensuales) / 1000))

        constitution = ctx.constitution
        comision = constitution.get("comisiones_plataforma", {}).get("mercadolibre_cl_pct", 13)

        data = envelope(
            "FinancialAgent",
            confidence=0.58,
            error_margin_pct=25,
            metrics={
                "margen_neto_pct": metric(lo, hi, pt),
                "break_even_clientes": metric(2, 15, 5),
                "comision_plataforma_pct": metric(comision - 2, comision + 2, comision),
            },
            findings=[f"Unit economics tipo {tipo}", "Rangos min/max — no punto único"],
            warnings=["Validar con 3 clientes reales antes de escalar"],
        )
        save_json(ctx.paths["financial"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["financial"])])

"""Agente 7 — Cost to MVP."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope, metric, tipo_negocio
from src.types import AgentResult, PipelineContext

SEMANAS = {"saas": (4, 10, 6), "servicio": (2, 6, 3), "ecommerce": (3, 8, 5), "marketplace": (6, 14, 9)}
COSTO_CLP = {"saas": (500_000, 3_000_000, 1_200_000), "servicio": (200_000, 1_500_000, 600_000)}


class CostToMvpAgent:
    key = "cost_mvp"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        idea = context.get("idea_normalizada", ctx.idea)
        tipo = context.get("tipo_negocio") or tipo_negocio(idea)
        sw = SEMANAS.get(tipo, (3, 8, 5))
        sc = COSTO_CLP.get(tipo, (300_000, 2_000_000, 800_000))
        mvp = idea.get("mvp") or []
        checklist = list(mvp) if mvp else ["Definir MVP en 1 página", "3 entrevistas cliente", "Prototipo funcional"]
        data = envelope(
            "CostToMvpAgent",
            confidence=0.62,
            error_margin_pct=30,
            metrics={
                "semanas": metric(*sw),
                "costo_clp": metric(*sc),
            },
            findings=[f"Complejidad: {'media' if sw[2] <= 6 else 'alta'}"],
            extra={"complejidad": "media" if sw[2] <= 6 else "alta", "checklist_mvp": checklist},
        )
        save_json(ctx.paths["cost_mvp"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["cost_mvp"])])

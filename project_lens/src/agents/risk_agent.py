"""Agente 8 — Risk."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope, tipo_negocio
from src.types import AgentResult, PipelineContext


class RiskAgent:
    key = "risk"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        tipo = context.get("tipo_negocio") or tipo_negocio(ctx.idea)
        riesgos = [
            {"categoria": "mercado", "severidad": 3, "probabilidad": 3, "mitigacion": "Validar con pilotos"},
            {"categoria": "tecnico", "severidad": 2, "probabilidad": 3, "mitigacion": "MVP acotado"},
        ]
        if tipo == "servicio":
            riesgos.insert(0, {"categoria": "plataforma", "severidad": 4, "probabilidad": 2, "mitigacion": "Cumplir políticas WhatsApp/Meta"})
        if tipo == "ecommerce":
            riesgos.insert(0, {"categoria": "proveedor", "severidad": 4, "probabilidad": 3, "mitigacion": "Semi-auto + stock mínimo"})
        max_sev = max(r["severidad"] for r in riesgos)
        data = envelope(
            "RiskAgent",
            confidence=0.6,
            error_margin_pct=15,
            findings=[f"Riesgo máximo severidad {max_sev}/5"],
            extra={"riesgos": riesgos, "severidad_max": max_sev},
        )
        save_json(ctx.paths["risk"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["risk"])])

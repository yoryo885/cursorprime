"""Agente 4 — Competition."""

from __future__ import annotations

from src.config import load_json, save_json
from src.agents.base import envelope, metric
from src.types import AgentResult, PipelineContext
from src.web_backend import search_competition


class CompetitionAgent:
    key = "competition"

    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = load_json(ctx.paths["context"], {}).get("idea_normalizada", ctx.idea)
        c = search_competition(idea, mock=ctx.mock_web, filters=ctx.constitution)

        is_mock = c.get("mock", ctx.mock_web)
        conf = 0.42 if is_mock else 0.78
        warnings = list(c.get("warnings") or [])
        if is_mock and not (idea.get("urls_referencia") or idea.get("competencia")):
            warnings.append("Añade urls_referencia o competencia[] en idea.json")
        elif is_mock and ctx.mock_web:
            warnings.append("MOCK_WEB=true — usa --no-mock-web para scrape real")

        n = c["num_competidores"]
        pmin, pmax = c["precio_min"], c["precio_max"]
        pmed = c.get("precio_mediana_clp", (pmin + pmax) / 2)
        filtros = c.get("filtros_aplicados", {})

        data = envelope(
            "CompetitionAgent",
            confidence=conf,
            error_margin_pct=18 if not is_mock else 30,
            metrics={
                "num_competidores": metric(max(1, n - 1), n + 1, n),
                "precio_clp": metric(pmin, pmax, pmed),
            },
            findings=[
                f"Saturación: {c['saturacion']}",
                f"URLs: {c.get('urls_procesadas', 0)}/{c.get('urls_solicitadas', 0)}",
                f"Precios usados: {c.get('precios_usados', 0)} (crudos: {c.get('precios_totales_detectados', 0)}, descartados: {c.get('precios_descartados_total', 0)})",
                f"Mediana mensual estimada: CLP {pmed:,}".replace(",", "."),
                f"Rango filtro: CLP {filtros.get('precio_clp_min', '?')}-{filtros.get('precio_clp_max', '?')}/mes",
            ],
            sources=c["sources"],
            warnings=warnings,
            extra={
                "saturacion": c["saturacion"],
                "competidores": c["competidores"],
                "mock": is_mock,
                "precio_mediana_clp": pmed,
                "filtros_aplicados": filtros,
            },
        )
        save_json(ctx.paths["competition"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["competition"])], warnings=warnings)

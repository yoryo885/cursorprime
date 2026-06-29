"""Agente: agrega scores y hallazgos de los 5 agentes."""

from __future__ import annotations

from datetime import datetime, timezone

from src.agents._utils import grade
from src.client_language import dedupe_findings, humanize_quick_wins
from src.config import agents_meta, load_json, plan_path, save_json
from src.types import AgentResult, PipelineContext

WEIGHTS_DEFAULT = {
    "content": 0.25,
    "conversion": 0.20,
    "technical": 0.20,
    "competitive": 0.15,
    "brand": 0.10,
    "growth": 0.10,
}


class SynthesisAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        plan = load_json(plan_path(), {})
        weights = plan.get("pesos_score") or WEIGHTS_DEFAULT
        discovery = load_json(ctx.paths["discovery"], {})
        context = load_json(ctx.paths["context"], {})
        agents_dir = agents_meta(ctx.slug)

        content = load_json(agents_dir / "content.json", {})
        conversion = load_json(agents_dir / "conversion.json", {})
        competitive = load_json(agents_dir / "competitive.json", {})
        technical = load_json(agents_dir / "technical.json", {})
        strategy = load_json(agents_dir / "strategy.json", {})

        brand = strategy.get("brand_score") or strategy.get("score", 50)
        growth = strategy.get("growth_score") or strategy.get("score", 50)

        categories = {
            "Content & Messaging": {"score": content.get("score", 0), "weight": "25%"},
            "Conversion Optimization": {"score": conversion.get("score", 0), "weight": "20%"},
            "SEO & Discoverability": {"score": technical.get("score", 0), "weight": "20%"},
            "Competitive Positioning": {"score": competitive.get("score", 0), "weight": "15%"},
            "Brand & Trust": {"score": brand, "weight": "10%"},
            "Growth & Strategy": {"score": growth, "weight": "10%"},
        }

        overall = round(
            content.get("score", 0) * weights.get("content", 0.25)
            + conversion.get("score", 0) * weights.get("conversion", 0.20)
            + technical.get("score", 0) * weights.get("technical", 0.20)
            + competitive.get("score", 0) * weights.get("competitive", 0.15)
            + brand * weights.get("brand", 0.10)
            + growth * weights.get("growth", 0.10)
        )

        all_findings: list[dict] = []
        for block in (content, conversion, competitive, technical, strategy):
            for f in block.get("findings") or []:
                all_findings.append({**f, "dimension": block.get("label")})

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_findings.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 9))
        client_findings = dedupe_findings(all_findings)[:12]

        payload = {
            "url": context.get("url"),
            "brand_name": context.get("brand_name"),
            "business_type": discovery.get("business_type"),
            "overall_score": overall,
            "grade": grade(overall),
            "categories": categories,
            "findings": client_findings,
            "competitors": competitive.get("competitors") or [],
            "quick_wins": humanize_quick_wins(client_findings),
            "mock": discovery.get("mock", False),
            "confidence": "medio" if discovery.get("mock") else "alto",
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(ctx.paths["synthesis"], payload)
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["synthesis"])],
            notes=f"Marketing Score: {overall}/100 ({payload['grade']})",
        )

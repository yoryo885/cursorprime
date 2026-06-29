"""Agente dimensión: Brand, Trust & Growth Strategy."""

from __future__ import annotations

from src.agents._utils import clamp_score
from src.config import load_json, save_json


class StrategyAgent:
    dimension = "strategy"
    label = "Brand & Growth Strategy"
    weight_key_brand = "brand"
    weight_key_growth = "growth"

    def analyze(self, discovery: dict) -> dict:
        trust = discovery.get("page_analysis", {}).get("trust", {})
        tracking = discovery.get("page_analysis", {}).get("tracking", {})
        social = trust.get("social_link_count") or 0
        schema = tracking.get("schema_count") or 0
        tools = tracking.get("tools_count") or 0

        brand = clamp_score(35 + social * 12 + schema * 10)
        growth = clamp_score(40 + tools * 15)

        findings = []
        if schema == 0:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Sin schema markup detectado",
                    "detail": "Añadir JSON-LD (Organization, FAQ) para rich results.",
                }
            )

        return {
            "dimension": "strategy",
            "label": self.label,
            "brand_score": brand,
            "growth_score": growth,
            "score": clamp_score(brand * 0.5 + growth * 0.5),
            "findings": findings,
            "wins": [],
            "confidence": "medio",
        }

    def run_file(self, discovery_path, output_path) -> dict:
        discovery = load_json(discovery_path, {})
        result = self.analyze(discovery)
        save_json(output_path, result)
        return result

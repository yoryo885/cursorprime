"""Agente dimensión: Conversion Optimization."""

from __future__ import annotations

from src.agents._utils import clamp_score
from src.config import load_json, save_json


class ConversionAgent:
    dimension = "conversion"
    label = "Conversion Optimization"
    weight_key = "conversion"

    def analyze(self, discovery: dict) -> dict:
        conv = discovery.get("page_analysis", {}).get("conversion", {})
        trust = discovery.get("page_analysis", {}).get("trust", {})
        cta_count = conv.get("cta_count") or 0
        forms = conv.get("form_count") or 0
        social = trust.get("social_link_count") or 0

        cta_score = min(95, 20 + cta_count * 18) if cta_count else 20
        form_score = 70 if forms == 1 else 50 if forms == 0 else 45
        trust_score = min(90, 30 + social * 15)

        raw = cta_score * 0.45 + form_score * 0.25 + trust_score * 0.3
        score = clamp_score(raw)

        findings = []
        if cta_count == 0:
            findings.append(
                {
                    "severity": "critical",
                    "title": "Sin CTAs detectados",
                    "detail": "Añadir CTA primario above the fold con beneficio claro.",
                }
            )
        elif cta_count == 1:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Un solo CTA",
                    "detail": "Considerar CTA secundario (demo, pricing) en páginas clave.",
                }
            )

        ctas = conv.get("ctas") or []
        wins = [f"CTA: {c.get('text', '')[:40]}" for c in ctas[:3]]

        return {
            "dimension": self.dimension,
            "label": self.label,
            "score": score,
            "findings": findings,
            "wins": wins,
            "confidence": "medio" if discovery.get("mock") else "alto",
        }

    def run_file(self, discovery_path, output_path) -> dict:
        discovery = load_json(discovery_path, {})
        result = self.analyze(discovery)
        save_json(output_path, result)
        return result

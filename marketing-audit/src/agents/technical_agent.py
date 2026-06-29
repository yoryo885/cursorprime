"""Agente dimensión: Technical SEO."""

from __future__ import annotations

from src.agents._utils import clamp_score
from src.config import load_json, save_json


class TechnicalAgent:
    dimension = "technical"
    label = "SEO & Discoverability"
    weight_key = "technical"

    def analyze(self, discovery: dict) -> dict:
        seo = discovery.get("page_analysis", {}).get("seo", {})
        scores = discovery.get("page_analysis", {}).get("scores", {})
        base = scores.get("seo", 5) * 10

        if not seo.get("has_viewport"):
            base -= 15
        if seo.get("images_without_alt", 0) > 0:
            base -= min(20, seo.get("images_without_alt", 0) * 5)
        if not seo.get("meta_description"):
            base -= 20
        if not (seo.get("headings", {}).get("h1") or []):
            base -= 15

        score = clamp_score(base)
        findings = []
        if not seo.get("meta_description"):
            findings.append(
                {
                    "severity": "high",
                    "title": "Meta description ausente",
                    "detail": "Escribir meta única por página principal (150-160 chars).",
                }
            )
        if seo.get("images_without_alt", 0) > 0:
            findings.append(
                {
                    "severity": "medium",
                    "title": f"{seo['images_without_alt']} imágenes sin alt",
                    "detail": "Añadir alt descriptivo para accesibilidad y SEO.",
                }
            )

        return {
            "dimension": self.dimension,
            "label": self.label,
            "score": score,
            "findings": findings,
            "wins": ["Viewport móvil OK"] if seo.get("has_viewport") else [],
            "confidence": "alto" if not discovery.get("mock") else "medio",
        }

    def run_file(self, discovery_path, output_path) -> dict:
        discovery = load_json(discovery_path, {})
        result = self.analyze(discovery)
        save_json(output_path, result)
        return result

"""Agente dimensión: Content & Messaging."""

from __future__ import annotations

from src.agents._utils import clamp_score, severity_from_score
from src.config import load_json


class ContentAgent:
    dimension = "content"
    label = "Content & Messaging"
    weight_key = "content"

    def analyze(self, discovery: dict) -> dict:
        seo = discovery.get("page_analysis", {}).get("seo", {})
        h1s = seo.get("headings", {}).get("h1") or []
        title = seo.get("title") or ""
        meta = seo.get("meta_description") or ""
        word_count = discovery.get("page_analysis", {}).get("word_count") or 0

        headline = 70 if h1s and len(h1s[0]) > 12 else 35 if h1s else 15
        value_prop = 65 if title and len(title) > 20 else 40
        copy_depth = min(90, 40 + word_count // 20) if word_count else 45
        meta_score = 75 if meta and len(meta) > 50 else 25 if not meta else 50

        raw = headline * 0.3 + value_prop * 0.25 + copy_depth * 0.25 + meta_score * 0.2
        score = clamp_score(raw)

        findings = []
        if not meta:
            findings.append(
                {
                    "severity": "critical",
                    "title": "Sin meta description",
                    "detail": "Google autogenera snippets — baja CTR en búsqueda.",
                }
            )
        if not h1s:
            findings.append(
                {
                    "severity": "high",
                    "title": "Sin H1 claro",
                    "detail": "Añadir un H1 que comunique valor en 5 segundos.",
                }
            )

        return {
            "dimension": self.dimension,
            "label": self.label,
            "score": score,
            "findings": findings,
            "wins": [f"Título presente: {title[:60]}"] if title else [],
            "confidence": "medio" if discovery.get("mock") else "alto",
        }

    def run_file(self, discovery_path, output_path) -> dict:
        discovery = load_json(discovery_path, {})
        result = self.analyze(discovery)
        from src.config import save_json

        save_json(output_path, result)
        return result

"""Agente dimensión: Competitive Positioning."""

from __future__ import annotations

from src.agents._utils import clamp_score
from src.config import MAX_COMPETITORS, MOCK_FETCH, load_json, save_json


MOCK_COMPETITORS = [
    {"name": "Competitor A", "url": "https://example-a.com", "tier": "direct"},
    {"name": "Competitor B", "url": "https://example-b.com", "tier": "direct"},
    {"name": "Market Leader", "url": "https://example-leader.com", "tier": "aspirational"},
]


def _search_competitors(domain: str, business_type: str) -> list[dict]:
    if MOCK_FETCH:
        return [{**c, "note": "mock"} for c in MOCK_COMPETITORS]

    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return MOCK_COMPETITORS

    query = f"{domain} alternatives competitors"
    out: list[dict] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=MAX_COMPETITORS):
                out.append(
                    {
                        "name": (r.get("title") or "")[:80],
                        "url": r.get("href") or "",
                        "tier": "direct",
                        "snippet": (r.get("body") or "")[:200],
                    }
                )
    except Exception:
        return MOCK_COMPETITORS
    return out or MOCK_COMPETITORS


class CompetitiveAgent:
    dimension = "competitive"
    label = "Competitive Positioning"
    weight_key = "competitive"

    def analyze(self, discovery: dict) -> dict:
        from src.page_analyzer import domain_from_url

        url = discovery.get("url") or ""
        domain = domain_from_url(url)
        competitors = _search_competitors(domain, discovery.get("business_type", ""))

        # Heurística: pocos competidores encontrados o sin diferenciación en título
        title = discovery.get("page_analysis", {}).get("seo", {}).get("title") or ""
        diff_score = 70 if len(title) > 25 else 45
        comp_score = min(85, 40 + len(competitors) * 8)
        raw = diff_score * 0.6 + comp_score * 0.4
        score = clamp_score(raw)

        findings = [
            {
                "severity": "medium",
                "title": "Revisar página de alternativas / vs",
                "detail": "Comparar posicionamiento explícito vs competidores detectados.",
            }
        ]

        return {
            "dimension": self.dimension,
            "label": self.label,
            "score": score,
            "findings": findings,
            "competitors": competitors,
            "wins": [f"Competidor identificado: {c['name'][:40]}" for c in competitors[:2]],
            "confidence": "bajo" if discovery.get("mock") else "medio",
        }

    def run_file(self, discovery_path, output_path) -> dict:
        discovery = load_json(discovery_path, {})
        result = self.analyze(discovery)
        save_json(output_path, result)
        return result

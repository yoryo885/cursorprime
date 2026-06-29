"""Agente: fetch URL + analyze_page."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.page_analyzer import detect_business_type, fetch_and_analyze
from src.types import AgentResult, PipelineContext


class DiscoveryAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        url = context.get("url") or ""
        if not url:
            return AgentResult(ok=False, notes="Sin URL en context")

        page = fetch_and_analyze(url)
        business_type = context.get("business_type_hint") or detect_business_type(
            url, page
        )

        payload = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "business_type": business_type,
            "mock": page.get("mock", False),
            "page_analysis": page.get("analysis") or {},
            "fetch_error": page.get("fetch_error"),
        }
        save_json(ctx.paths["discovery"], payload)
        mode = "mock" if payload["mock"] else "live"
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["discovery"])],
            notes=f"Discovery {mode} — {business_type}",
        )

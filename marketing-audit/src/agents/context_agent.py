"""Agente: brief → context.json."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import branding_path, load_branding, load_json, save_json
from src.page_analyzer import domain_from_url
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = ctx.brief or load_json(ctx.paths["brief"], {}) or {}
        url = brief.get("url") or ""
        if not url:
            return AgentResult(ok=False, notes="brief.json requiere campo url")

        payload = {
            "slug": ctx.slug,
            "url": url if url.startswith("http") else f"https://{url}",
            "brand_name": brief.get("brand_name") or domain_from_url(url),
            "business_type_hint": brief.get("business_type"),
            "cliente": brief.get("cliente"),
            "proyecto": brief.get("proyecto"),
            "branding": load_branding(brief),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(ctx.paths["context"], payload)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["context"])], notes=payload["url"])

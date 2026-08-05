"""Manifest final."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = load_json(ctx.paths["brief"], {}) or {}
        manifest = {
            "slug": ctx.slug,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "estilo": brief.get("estilo"),
            "marca": brief.get("marca"),
            "archivos": {
                "preview": str(ctx.paths["preview"]),
                "brief": str(ctx.paths["output"] / "brief.md"),
                "ejemplos": str(ctx.paths["output"] / "ejemplos.md"),
            },
        }
        path = ctx.paths["output"] / "manifest.json"
        save_json(path, manifest)
        return AgentResult(ok=True, artifacts=[str(path)])

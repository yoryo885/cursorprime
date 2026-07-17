from __future__ import annotations

from src.config import kdp_listing_path, load_json, save_json, slug_meta
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        marca = load_json(ctx.paths["marca"], {}) or {}
        if not marca.get("marca"):
            return AgentResult(ok=False, notes="marca.json incompleto")
        kdp_path = kdp_listing_path(ctx.producto)
        kdp = load_json(kdp_path, {}) or {}
        if not kdp.get("titulo"):
            return AgentResult(ok=False, notes=f"KDP no encontrado: {kdp_path}")
        ctx.marca = marca
        ctx.kdp = kdp
        out = {
            "marca": marca.get("marca"),
            "producto": ctx.producto,
            "titulo_kdp": kdp.get("titulo"),
            "mock": ctx.mock,
            "modo_imagen": "mock" if ctx.mock else "openai",
        }
        save_json(slug_meta(ctx.slug) / "context.json", out)
        return AgentResult(ok=True, data=out)

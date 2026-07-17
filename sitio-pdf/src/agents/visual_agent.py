from __future__ import annotations

import json

from src.config import save_json, slug_meta, slug_output
from src.mock_assets import generate_mock_assets
from src.types import AgentResult, PipelineContext


class VisualAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        assets_dir = slug_output(ctx.slug) / "assets"
        if ctx.mock:
            raw = generate_mock_assets(assets_dir, ctx.marca, producto=ctx.producto)
            carousel = raw.pop("_carousel_json", [])
            ctx.assets = {k: v for k, v in raw.items() if isinstance(v, str)}
            save_json(slug_meta(ctx.slug) / "assets.json", {
                "modo": "mock",
                "files": ctx.assets,
                "carousel": carousel,
            })
            return AgentResult(ok=True, data={"carousel_count": len(carousel)}, warnings=["Mock SVG — activa OPENAI_API_KEY para imágenes reales"])
        return AgentResult(ok=False, notes="Modo OpenAI pendiente — usa --mock por ahora")

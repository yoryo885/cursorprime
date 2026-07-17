from __future__ import annotations

from src.config import save_json, slug_meta, slug_output
from src.mock_assets import generate_mock_assets
from src.types import AgentResult, PipelineContext


class VisualAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        assets_dir = slug_output(ctx.slug) / "assets"
        if ctx.mock:
            assets = generate_mock_assets(assets_dir, ctx.marca)
            ctx.assets = {k: f"assets/{v}" for k, v in assets.items()}
            save_json(slug_meta(ctx.slug) / "assets.json", {"modo": "mock", "files": ctx.assets})
            return AgentResult(ok=True, data=ctx.assets, warnings=["Mock SVG — activa OPENAI_API_KEY para imágenes reales"])
        return AgentResult(ok=False, notes="Modo OpenAI pendiente — usa --mock por ahora")

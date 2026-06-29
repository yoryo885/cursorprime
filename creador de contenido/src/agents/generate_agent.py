"""Agente 4: genera imágenes (mock Pillow o API futura)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.image_backend import generate_placeholder
from src.types import AgentResult, PipelineContext


class GenerateAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        style = load_json(ctx.paths["style"], {})
        data = load_json(ctx.paths["prompts"], {})
        warnings = []

        generated = []
        img_dir = ctx.paths["imagenes"]
        img_dir.mkdir(parents=True, exist_ok=True)

        for item in data.get("prompts", []):
            path = img_dir / item["archivo"]
            if ctx.mock_generate:
                generate_placeholder(
                    path,
                    titulo=context.get("titulo", ctx.slug),
                    tema=item["tema"],
                    palette=style.get("palette", []),
                )
            else:
                warnings.append("API real no configurada — usar MOCK_GENERATE=true")
                generate_placeholder(path, context.get("titulo", ""), item["tema"], style.get("palette", []))

            generated.append(
                {
                    "tema": item["tema"],
                    "archivo": item["archivo"],
                    "path": str(path),
                    "prompt": item["prompt"],
                    "generado_at": datetime.now(timezone.utc).isoformat(),
                    "mock": ctx.mock_generate,
                }
            )

        out = ctx.paths["generated"]
        save_json(out, {"imagenes": generated, "count": len(generated)})
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(generated)} imágenes", warnings=warnings)


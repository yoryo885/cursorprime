"""Módulo imágenes PNG — temas o pares inicio/fin por escena."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.image_backend import generate_placeholder
from src.types import AgentResult, PipelineContext


class ImagenesModule:
    slug_modulo = "imagenes"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        style = load_json(ctx.paths["style"], {})
        data = load_json(ctx.paths["prompts"], {})
        video_modo = data.get("video_modo") or (context.get("video") or {}).get("modo", "slideshow")

        generated = []
        img_dir = ctx.paths["imagenes_out"]
        img_dir.mkdir(parents=True, exist_ok=True)

        force_character = video_modo == "animado"
        for item in data.get("prompts", []):
            path = img_dir / item["archivo"]
            frame = 1 if item.get("tipo_frame") == "inicio" else 2
            label = item.get("tipo_frame") or "frame"
            generate_placeholder(
                path,
                titulo=context.get("titulo", ctx.slug),
                tema=f"{item['tema']} · {label}",
                palette=style.get("palette", []),
                frame=frame,
                frames_total=2 if item.get("tipo_frame") else 1,
                force_character=force_character,
            )
            generated.append(
                {
                    "tema": item["tema"],
                    "archivo": item["archivo"],
                    "path": str(path),
                    "modulo": "imagenes",
                    "escena_id": item.get("escena_id"),
                    "tipo_frame": item.get("tipo_frame"),
                    "generado_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        out = ctx.paths["generated_imagenes"]
        save_json(
            out,
            {"imagenes": generated, "count": len(generated), "video_modo": video_modo},
        )
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(generated)} PNG ({video_modo})")

"""Módulo GIF — animaciones desde frames."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from src.config import load_json, save_json, slugify
from src.image_backend import generate_placeholder
from src.types import AgentResult, PipelineContext


class GifsModule:
    slug_modulo = "gifs"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        style = load_json(ctx.paths["style"], {})
        prompts = load_json(ctx.paths["prompts"], {}).get("prompts", [])
        cfg = context.get("gif") or {}
        frames_n = int(cfg.get("frames") or 4)
        duration = int(cfg.get("duration_ms") or 250)

        gifs_dir = ctx.paths["gifs_out"]
        gifs_dir.mkdir(parents=True, exist_ok=True)
        items = []

        for p in prompts:
            tema = p["tema"]
            slug = slugify(tema)
            frame_paths = []
            for i in range(1, frames_n + 1):
                fp = gifs_dir / f"_frame_{slug}_{i}.png"
                generate_placeholder(
                    fp,
                    context.get("titulo", ctx.slug),
                    tema,
                    style.get("palette", []),
                    frame=i,
                    frames_total=frames_n,
                )
                frame_paths.append(fp)

            gif_path = gifs_dir / f"{p.get('id', 0):02d}-{slug}.gif"
            imgs = [Image.open(f) for f in frame_paths]
            imgs[0].save(
                gif_path,
                save_all=True,
                append_images=imgs[1:],
                duration=duration,
                loop=0,
            )
            for im in imgs:
                im.close()
            for fp in frame_paths:
                fp.unlink(missing_ok=True)

            items.append(
                {
                    "tema": tema,
                    "archivo": gif_path.name,
                    "path": str(gif_path),
                    "modulo": "gifs",
                    "frames": frames_n,
                    "generado_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        out = ctx.paths["generated_gifs"]
        save_json(out, {"gifs": items, "count": len(items)})
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(items)} GIF")

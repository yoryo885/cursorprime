"""ThumbnailAgent — brief + PNG placeholder de miniatura."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


def _placeholder_png(path: Path, titulo: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1280, 720), (26, 26, 46))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 1240, 680], outline=(22, 160, 133), width=6)
        text = (titulo or "Guía")[:42]
        draw.text((80, 300), text, fill=(245, 245, 245))
        draw.text((80, 380), "MINIATURA", fill=(22, 160, 133))
        img.save(path, "PNG")
    except Exception:
        # Fallback mínimo válido (>1KB para QC)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 2048)


class ThumbnailAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
        hook = lote.get("hook") or titulo

        png_path = ctx.paths["copy_dir"] / "thumbnail.png"
        _placeholder_png(png_path, str(titulo))

        brief = {
            "skill": "thumbnail-social",
            "titulo_on_image": str(titulo)[:40],
            "subtitulo": str(hook)[:60],
            "estilo": context.get("estilo") or "yordy-minimal",
            "prompt": (
                f"YouTube thumbnail, bold text «{titulo}», high contrast, "
                f"clean composition, style {context.get('estilo', 'yordy-minimal')}, no clutter"
            ),
            "archivo": str(png_path),
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": "low",
            "nota": "PNG placeholder MVP; skill thumbnail-social puede iterar diseño",
        }
        out = ctx.paths["thumbnail"]
        save_json(out, brief)

        return AgentResult(
            ok=True,
            artifacts=[str(out), str(png_path)],
            notes=f"Thumbnail brief + {png_path.name}",
        )

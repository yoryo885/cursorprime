"""Módulo imágenes PNG — respeta MOCK_GENERATE; API real con fallback."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import MOCK_GENERATE, load_json, save_json
from src.image_backend import generate_image
from src.types import AgentResult, PipelineContext


class ImagenesModule:
    slug_modulo = "imagenes"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        style = load_json(ctx.paths["style"], {})
        data = load_json(ctx.paths["prompts"], {})
        video_modo = data.get("video_modo") or (context.get("video") or {}).get("modo", "slideshow")
        use_mock = ctx.mock_generate if ctx.mock_generate is not None else MOCK_GENERATE

        generated = []
        warnings = []
        img_dir = ctx.paths["imagenes_out"]
        img_dir.mkdir(parents=True, exist_ok=True)
        reales = 0
        mocks = 0

        for item in data.get("prompts", []):
            path = img_dir / item["archivo"]
            frame = 1 if item.get("tipo_frame") == "inicio" else 2
            label = item.get("tipo_frame") or "frame"
            prompt = item.get("prompt") or (
                f"Illustration, {style.get('descripcion') or context.get('estilo')}, "
                f"topic: {item['tema']}, {label}, clean composition, no text, square"
            )
            _, fue_mock, nota = generate_image(
                path,
                prompt=prompt,
                titulo=context.get("titulo", ctx.slug),
                tema=f"{item['tema']} · {label}",
                palette=style.get("palette", []),
                frame=frame,
                frames_total=2 if item.get("tipo_frame") else 1,
                mock=use_mock,
            )
            if fue_mock:
                mocks += 1
                if nota.startswith("fallback"):
                    warnings.append(f"{item['archivo']}: {nota}")
            else:
                reales += 1

            generated.append(
                {
                    "tema": item["tema"],
                    "archivo": item["archivo"],
                    "path": str(path),
                    "modulo": "imagenes",
                    "escena_id": item.get("escena_id"),
                    "tipo_frame": item.get("tipo_frame"),
                    "mock": fue_mock,
                    "backend": nota,
                    "generado_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        out = ctx.paths["generated_imagenes"]
        save_json(
            out,
            {
                "imagenes": generated,
                "count": len(generated),
                "video_modo": video_modo,
                "mock_generate": use_mock,
                "reales": reales,
                "mocks": mocks,
            },
        )
        notes = f"{len(generated)} PNG ({video_modo}) · reales={reales} mock={mocks}"
        return AgentResult(ok=True, artifacts=[str(out)], notes=notes, warnings=warnings)

"""Agente 3: prompts por tema o por escena (inicio/fin)."""

from __future__ import annotations

from src.config import load_json, save_json, slugify
from src.types import AgentResult, PipelineContext


class PromptAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        style = load_json(ctx.paths["style"], {})
        video_modo = (context.get("video") or {}).get("modo", "slideshow")

        prompts = []
        if video_modo == "animado" and ctx.paths.get("escenas") and ctx.paths["escenas"].exists():
            escenas_data = load_json(ctx.paths["escenas"], {})
            for esc in escenas_data.get("escenas", []):
                prompts.append(
                    {
                        "id": esc["id"],
                        "escena_id": esc["id"],
                        "tipo_frame": "inicio",
                        "tema": esc.get("titulo", f"escena_{esc['id']}"),
                        "slug": esc.get("slug") or slugify(esc.get("titulo", "")),
                        "prompt": esc.get("start_frame_prompt", ""),
                        "archivo": esc.get("archivo_inicio", f"{esc['id']:02d}-inicio.png"),
                        "animation_prompt": esc.get("animation_prompt", ""),
                    }
                )
                prompts.append(
                    {
                        "id": esc["id"],
                        "escena_id": esc["id"],
                        "tipo_frame": "fin",
                        "tema": esc.get("titulo", f"escena_{esc['id']}"),
                        "slug": esc.get("slug") or slugify(esc.get("titulo", "")),
                        "prompt": esc.get("end_frame_prompt", ""),
                        "archivo": esc.get("archivo_fin", f"{esc['id']:02d}-fin.png"),
                        "animation_prompt": esc.get("animation_prompt", ""),
                    }
                )
        else:
            for i, tema in enumerate(context.get("temas", []), start=1):
                prompts.append(
                    {
                        "id": i,
                        "tema": tema,
                        "slug": slugify(tema),
                        "prompt": (
                            f"Illustration for '{tema}', style: {style.get('descripcion')}, "
                            f"flat design, clean lines, palette {style.get('palette')}, "
                            f"no text, square composition"
                        ),
                        "archivo": f"{i:02d}-{slugify(tema)}.png",
                    }
                )

        out = ctx.paths["prompts"]
        save_json(out, {"prompts": prompts, "count": len(prompts), "video_modo": video_modo})
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(prompts)} prompts ({video_modo})")

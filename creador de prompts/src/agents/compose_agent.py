"""Agente 3: compone prompts desde plantilla + temas."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json, slugify
from src.types import AgentResult, PipelineContext


def _fmt(template: str, mapping: dict) -> str:
    out = template
    for key, val in mapping.items():
        out = out.replace("{" + key + "}", str(val))
    return out


class ComposeAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        plantilla = load_json(ctx.paths["plantilla"], {})
        tpl = plantilla.get("template", "{tema}")
        tpl_neg = plantilla.get("negative", "")
        ctx_extra = context.get("contexto") or {}

        base = {
            "titulo": context.get("titulo", ctx.slug),
            "proyecto": context.get("proyecto_nombre", "General"),
            "tipo": context.get("tipo", ""),
            "audiencia": ctx_extra.get("audiencia", "público general"),
            "tono": ctx_extra.get("tono", "claro y profesional"),
            "estilo": ctx_extra.get("estilo", "minimal"),
            "idioma": ctx_extra.get("idioma", "español"),
            "objetivo": ctx_extra.get("objetivo", "informar"),
        }

        prompts = []
        for i, tema in enumerate(context.get("temas", []), start=1):
            mapping = {**base, "tema": tema, "slug": slugify(tema)}
            for v in range(1, int(context.get("variantes") or 1) + 1):
                suffix = f" v{v}" if context.get("variantes", 1) > 1 else ""
                prompts.append(
                    {
                        "id": len(prompts) + 1,
                        "tema": tema,
                        "variante": v,
                        "tipo": context.get("tipo"),
                        "proyecto_destino": context.get("proyecto_destino"),
                        "prompt": _fmt(tpl, mapping).strip() + suffix,
                        "negative": _fmt(tpl_neg, mapping).strip() if tpl_neg else "",
                        "archivo_sugerido": f"{i:02d}-{slugify(tema)}.md",
                        "generado_at": datetime.now(timezone.utc).isoformat(),
                    }
                )

        out = ctx.paths["prompts"]
        save_json(out, {"prompts": prompts, "count": len(prompts), "plantilla": plantilla.get("id")})
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(prompts)} prompts")

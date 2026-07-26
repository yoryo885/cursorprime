"""CaptionsAgent — copy redes (promo o enseñanza)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.formato import formato_video
from src.types import AgentResult, PipelineContext


class CaptionsAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        formato = formato_video(lote, context)
        titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
        hook = lote.get("hook") or ""
        guia = lote.get("guia") if isinstance(lote.get("guia"), dict) else {}

        if formato == "ensenanza":
            cta = guia.get("cierre") or lote.get("cierre") or "Guarda esto para cuando te sientas disperso."
            caption = (
                f"{hook}\n\n"
                f"Una enseñanza clara de «{titulo}».\n"
                f"{cta}\n\n"
                f"#aprendizaje #productividad #pareto #psicologia"
            ).strip()
            hashtags = ["aprendizaje", "productividad", "pareto", "ensenanza"]
        else:
            cta = guia.get("cta") or lote.get("cta") or f"Comenta GUÍA y te paso el enlace a «{titulo}»."
            caption = (
                f"{hook}\n\n"
                f"En este video resumo lo esencial de «{titulo}».\n"
                f"{cta}\n\n"
                f"#guia #productividad #aprendizaje"
            ).strip()
            hashtags = ["guia", "productividad", "aprendizaje"]

        payload = {
            "skill": "captions-redes",
            "formato": formato,
            "plataforma": lote.get("plataforma") or "reels",
            "caption": caption,
            "hashtags": hashtags,
            "cta": cta,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": "medium",
        }
        out = ctx.paths["captions"]
        save_json(out, payload)
        md = ctx.paths["copy_dir"] / "captions.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(f"# Caption ({formato}) — {titulo}\n\n{caption}\n", encoding="utf-8")

        return AgentResult(ok=True, artifacts=[str(out), str(md)], notes=f"Caption {formato} listo")

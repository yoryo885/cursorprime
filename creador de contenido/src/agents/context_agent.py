"""Agente: normaliza lote y salidas solicitadas."""

from __future__ import annotations

from src.config import load_json, normalizar_salidas, salidas_con_dependencias, save_json
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        raw = load_json(ctx.paths["lote"], {}) or ctx.lote
        temas = raw.get("temas") or []
        cantidad = int(raw.get("cantidad") or len(temas) or 1)
        if not temas and cantidad:
            temas = [f"tema_{i+1}" for i in range(cantidad)]

        salidas_pedidas = normalizar_salidas(raw)
        salidas_efectivas = salidas_con_dependencias(salidas_pedidas)

        video_cfg = raw.get("video") or {}
        video_modo = (video_cfg.get("modo") or "slideshow").lower()
        if video_modo not in ("slideshow", "animado"):
            video_modo = "slideshow"

        context = {
            "slug": ctx.slug,
            "titulo": raw.get("titulo") or ctx.slug,
            "cantidad": len(temas),
            "salidas_pedidas": salidas_pedidas,
            "salidas_efectivas": salidas_efectivas,
            "estilo": raw.get("estilo") or "yordy-minimal",
            "temas": temas,
            "guion": raw.get("guion", ""),
            "uso": raw.get("uso", "general"),
            "gif": raw.get("gif") or {},
            "video": {**video_cfg, "modo": video_modo},
            "pdf": raw.get("pdf") or {},
            "notas": raw.get("notas", ""),
        }

        ctx.salidas = salidas_efectivas
        save_json(ctx.paths["context"], context)
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["context"])],
            notes=f"Salidas: {', '.join(salidas_pedidas)} → {', '.join(salidas_efectivas)}",
        )

"""Agente: normaliza lote y salidas solicitadas."""

from __future__ import annotations

from src.config import load_json, normalizar_salidas, salidas_con_dependencias, save_json
from src.recipes import infer_receta, resolve_recipe
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        raw = load_json(ctx.paths["lote"], {}) or ctx.lote
        temas = raw.get("temas") or []
        cantidad = int(raw.get("cantidad") or len(temas) or 1)
        if not temas and cantidad:
            temas = [f"tema_{i+1}" for i in range(cantidad)]

        guia = raw.get("guia") if isinstance(raw.get("guia"), dict) else {}
        if guia.get("temas") and not raw.get("temas"):
            temas = list(guia["temas"])

        receta = raw.get("receta") or getattr(ctx, "receta", None) or infer_receta(raw)
        plan_preview = resolve_recipe({**raw, "receta": receta}, receta)
        salidas_pedidas = list(plan_preview.get("salidas") or normalizar_salidas(raw))
        salidas_efectivas = salidas_con_dependencias(salidas_pedidas)

        video_cfg = dict(plan_preview.get("video") or raw.get("video") or {})
        video_modo = (video_cfg.get("modo") or "slideshow").lower()
        if video_modo not in ("slideshow", "animado"):
            video_modo = "slideshow"

        context = {
            "slug": ctx.slug,
            "titulo": raw.get("titulo") or guia.get("titulo") or ctx.slug,
            "cantidad": len(temas),
            "salidas_pedidas": salidas_pedidas,
            "salidas_efectivas": salidas_efectivas,
            "estilo": raw.get("estilo") or "yordy-minimal",
            "temas": temas,
            "guion": raw.get("guion", ""),
            "guia": guia,
            "fuente_guia": raw.get("fuente_guia") or guia.get("fuente") or "",
            "uso": raw.get("uso", "general"),
            "receta": receta,
            "copy": raw.get("copy") or [],
            "gif": raw.get("gif") or {},
            "video": {**video_cfg, "modo": video_modo},
            "pdf": raw.get("pdf") or {},
            "notas": raw.get("notas", ""),
        }

        # Persistir receta inferida en lote
        if not raw.get("receta"):
            raw = {**raw, "receta": receta}
            save_json(ctx.paths["lote"], raw)

        ctx.salidas = salidas_efectivas
        ctx.lote = raw
        ctx.receta = receta
        save_json(ctx.paths["context"], context)
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["context"])],
            notes=f"Receta: {receta} · salidas: {', '.join(salidas_pedidas)} → {', '.join(salidas_efectivas)}",
        )

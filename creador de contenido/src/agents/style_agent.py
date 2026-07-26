"""Agente: perfil de estilo visual (promo vs ensenanza blob)."""

from __future__ import annotations

from src.config import load_json, save_json
from src.formato import formato_video
from src.types import AgentResult, PipelineContext


class StyleAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        formato = formato_video(lote, context)
        estilo_id = context.get("estilo") or lote.get("estilo") or "yordy-minimal"
        estilos = ctx.constitution.get("estilos", {})
        perfil = estilos.get(estilo_id, estilos.get("yordy-minimal", {}))

        if formato == "ensenanza":
            descripcion = (
                str(lote.get("estilo") or "")
                or "faceless educativo estilo Psicología Invisible: personaje blob/cápsula "
                "gris-verde, brazos finos, escenarios pastel, banner título amarillo, "
                "ilustración plana suave, sin hard sell, vertical 9:16"
            )
            palette = ["#F5E6C8", "#F5C518", "#6B7F6A", "#2C2C2C"]
            notes = "ensenanza-blob"
        else:
            descripcion = perfil.get("descripcion", "Estilo minimal")
            palette = perfil.get("palette", ["#1a1a2e", "#16a085", "#f5f5f5"])
            notes = str(estilo_id)

        style = {
            "estilo_id": estilo_id if formato != "ensenanza" else "psico-invisible-blob",
            "formato_video": formato,
            "descripcion": descripcion,
            "palette": palette,
            "formato": context.get("formato", "png"),
            "personaje_fijo": formato == "ensenanza",
            "reglas": [
                "Mismo personaje en todas las escenas",
                "Banner de título corto en cada escena",
                "Sin mock placeholder de texto plano",
            ]
            if formato == "ensenanza"
            else [],
        }

        out = ctx.paths["style"]
        save_json(out, style)
        context["estilo"] = style["estilo_id"]
        context["formato"] = formato
        save_json(ctx.paths["context"], context)
        return AgentResult(ok=True, artifacts=[str(out)], notes=notes)

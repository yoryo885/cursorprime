"""Agente 2: perfil de estilo visual."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class StyleAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        estilo_id = context.get("estilo", "yordy-minimal")
        estilos = ctx.constitution.get("estilos", {})
        perfil = estilos.get(estilo_id, estilos.get("yordy-minimal", {}))

        style = {
            "estilo_id": estilo_id,
            "descripcion": perfil.get("descripcion", "Estilo minimal"),
            "palette": perfil.get("palette", ["#1a1a2e", "#16a085", "#f5f5f5"]),
            "formato": context.get("formato", "png"),
        }

        out = ctx.paths["style"]
        save_json(out, style)
        return AgentResult(ok=True, artifacts=[str(out)], notes=estilo_id)


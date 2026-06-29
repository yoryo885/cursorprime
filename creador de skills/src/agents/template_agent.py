"""Agente 2: plantilla por tipo."""

from __future__ import annotations

from src.config import PLANTILLAS_DIR, load_json, save_json
from src.types import AgentResult, PipelineContext


class TemplateAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        tipo = context.get("tipo", "workflow")
        path = PLANTILLAS_DIR / f"{tipo}.json"
        if not path.exists():
            return AgentResult(ok=False, notes=f"Plantilla no encontrada: {tipo}")
        plantilla = load_json(path, {})
        save_json(ctx.paths["plantilla"], plantilla)
        return AgentResult(ok=True, notes=plantilla.get("nombre", tipo))

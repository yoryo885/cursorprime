"""Agente 2: selecciona plantilla por tipo."""

from __future__ import annotations

from src.config import PLANTILLAS_DIR, load_json, save_json
from src.types import AgentResult, PipelineContext


class TemplateAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        tipo = context.get("tipo", "imagen")
        path = PLANTILLAS_DIR / f"{tipo}.json"

        if not path.exists():
            return AgentResult(ok=False, notes=f"Plantilla no encontrada: {tipo}")

        plantilla = load_json(path, {})
        out = ctx.paths["plantilla"]
        save_json(out, plantilla)
        return AgentResult(
            ok=True,
            artifacts=[str(out)],
            notes=plantilla.get("nombre", tipo),
        )

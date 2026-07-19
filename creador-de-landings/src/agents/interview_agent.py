"""Carga o corre entrevista."""

from __future__ import annotations

from src.config import load_json, save_json
from src.interview import load_or_interview
from src.types import AgentResult, PipelineContext


class InterviewAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        interactive = bool(ctx.respuestas.get("_interactive"))
        force = bool(ctx.respuestas.get("_force_interview"))
        prefill = {k: v for k, v in ctx.respuestas.items() if not k.startswith("_")}
        if prefill and not force:
            save_json(ctx.paths["respuestas"], prefill)
            data = prefill
        else:
            data = load_or_interview(ctx.slug, interactive=interactive, force=force)
        ctx.respuestas = data
        return AgentResult(ok=True, artifacts=[str(ctx.paths["respuestas"])], notes="entrevista ok")

"""Genera preview.html."""

from __future__ import annotations

from src.config import load_json
from src.templates.html_builder import build_html
from src.types import AgentResult, PipelineContext


class BuildAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = load_json(ctx.paths["brief"], {}) or {}
        if not brief:
            return AgentResult(ok=False, notes="Falta brief.json")
        html = build_html(brief)
        out = ctx.paths["preview"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"     HTML → {out}")
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"estilo={brief.get('estilo')}")

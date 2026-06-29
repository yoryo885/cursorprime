"""QC — investigación."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class QcInvestigacionAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        analisis = load_json(ctx.paths["analisis"], {})
        issues = []

        if not analisis.get("fuentes"):
            issues.append("Sin fuentes citadas")
        if len(analisis.get("productos_que_funcionan") or []) < 1:
            issues.append("Sin productos identificados")
        if not analisis.get("oportunidades_pipeline"):
            issues.append("Sin oportunidades de pipeline")

        qc = {
            "ok": len(issues) == 0,
            "issues": issues,
            "fuentes_count": len(analisis.get("fuentes") or []),
        }
        save_json(ctx.paths["qc"], qc)
        return AgentResult(ok=qc["ok"], notes="QC ok" if qc["ok"] else "; ".join(issues))

"""QC — lluvia de ideas."""

from __future__ import annotations

from src.config import CATEGORIAS_IDEA, load_json, save_json
from src.types import AgentResult, PipelineContext


class QcLluviaAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        data = load_json(ctx.paths["ideas"], {})
        ideas = data.get("ideas") or []
        issues = []

        for i, idea in enumerate(ideas):
            prefix = f"idea[{i}]"
            if idea.get("categoria") not in CATEGORIAS_IDEA:
                issues.append(f"{prefix}: categoría inválida")
            for field in ("titulo", "propuesta", "proyecto_afectado"):
                if not idea.get(field):
                    issues.append(f"{prefix}: falta {field}")
            if idea.get("estado") != "pendiente_aprobacion":
                issues.append(f"{prefix}: estado debe ser pendiente_aprobacion")

        qc = {"ok": len(issues) == 0, "issues": issues, "ideas_count": len(ideas)}
        save_json(ctx.paths["qc"], qc)
        return AgentResult(ok=qc["ok"], notes=f"{len(ideas)} ideas QC")

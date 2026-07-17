from __future__ import annotations

from src.config import save_json, slug_meta
from src.types import AgentResult, PipelineContext


class QCAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        issues = []
        warnings = []
        required_assets = ["portada", "mockup_movil"]
        for key in required_assets:
            if key not in ctx.assets:
                issues.append(f"Falta asset: {key}")
        if not ctx.copy.get("product", {}).get("titulo"):
            issues.append("Copy producto vacío")
        if not ctx.marca.get("colores"):
            warnings.append("Paleta de marca no definida")
        report = {
            "ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "assets": list(ctx.assets.keys()),
        }
        save_json(slug_meta(ctx.slug) / "qc_report.json", report)
        if issues:
            return AgentResult(ok=False, notes="; ".join(issues), warnings=warnings)
        return AgentResult(ok=True, warnings=warnings, data=report)

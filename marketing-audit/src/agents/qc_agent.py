"""QC del audit."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        synthesis = load_json(ctx.paths["synthesis"], {})
        warnings: list[str] = []
        ok = True

        if not synthesis.get("url"):
            ok = False
            warnings.append("Sin URL en synthesis")
        if synthesis.get("overall_score") is None:
            ok = False
            warnings.append("Sin score overall")
        if synthesis.get("mock"):
            warnings.append("Datos MOCK — re-ejecutar con MOCK_FETCH=false para live")
        if not synthesis.get("findings"):
            warnings.append("Sin hallazgos — revisar discovery")

        payload = {
            "ok": ok,
            "warnings": warnings,
            "score": synthesis.get("overall_score"),
            "qc_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(ctx.paths["qc"], payload)
        return AgentResult(ok=ok, artifacts=[str(ctx.paths["qc"])], warnings=warnings)

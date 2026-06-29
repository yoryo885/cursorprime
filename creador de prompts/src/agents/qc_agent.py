"""QC de prompts generados."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext

MIN_LEN = 20


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        data = load_json(ctx.paths["prompts"], {})
        issues = []
        passed = []

        for item in data.get("prompts", []):
            text = item.get("prompt", "")
            if len(text) < MIN_LEN:
                issues.append({"id": item.get("id"), "error": "prompt muy corto"})
            elif "{" in text and "}" in text:
                issues.append({"id": item.get("id"), "error": "placeholders sin reemplazar"})
            else:
                passed.append(item.get("archivo_sugerido", str(item.get("id"))))

        ok = len(issues) == 0 and len(passed) > 0
        result = {"ok": ok, "passed": passed, "issues": issues}
        save_json(ctx.paths["qc"], result)
        return AgentResult(ok=ok, artifacts=[str(ctx.paths["qc"])], notes=f"QC {len(passed)} OK")

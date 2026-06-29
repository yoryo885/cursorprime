"""QC de skills generadas."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext

MAX_LINES = 500
MIN_DESC = 30


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        composed = load_json(ctx.paths["composed"], {})
        skill_path = ctx.paths["skill_md"]
        text = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
        issues = []

        if not text.startswith("---"):
            issues.append("falta frontmatter YAML")
        if "name:" not in text[:300]:
            issues.append("falta name en frontmatter")
        if "description:" not in text[:400]:
            issues.append("falta description")
        desc = composed.get("description", "")
        if len(desc) < MIN_DESC:
            issues.append("description muy corta")
        if composed.get("line_count", 0) > MAX_LINES:
            issues.append(f"SKILL.md > {MAX_LINES} líneas — mover detalle a reference.md")
        if not composed.get("triggers"):
            issues.append("sin triggers — difícil auto-descubrimiento")

        ok = len(issues) == 0 or (len(issues) == 1 and "triggers" in issues[0])
        result = {"ok": ok, "issues": issues, "warnings": issues if not ok else []}
        save_json(ctx.paths["qc"], result)
        return AgentResult(ok=ok, notes=f"QC {'OK' if ok else issues}")

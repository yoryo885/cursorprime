"""Agente 11 — QC."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class QCAgent:
    key = "qc"

    def run(self, ctx: PipelineContext) -> AgentResult:
        issues = []
        passed = []
        verdict = load_json(ctx.paths["synthesis"], {})
        plan_path = ctx.paths.get("planner")
        plan = load_json(plan_path, {}) if plan_path else {}

        # Solo agentes web requieren sources explícitas
        for key in ("trend", "market", "competition"):
            p = ctx.paths.get(key)
            if not p or not p.exists():
                continue
            d = load_json(p, {})
            if d.get("metrics") and not d.get("sources"):
                issues.append({"agent": key, "error": "métricas sin sources"})
            elif d.get("confidence", 0) > 0.8 and len(d.get("sources", [])) < 2:
                issues.append({"agent": key, "error": "confidence alta con pocas fuentes"})
            else:
                passed.append(key)

        if verdict.get("veredicto") == "viable" and verdict.get("confidence_global", 0) < 0.5:
            issues.append({"error": "viable con confidence_global baja"})

        sem_plan = sum(f.get("semanas", 0) for f in plan.get("fases", []))
        cost = load_json(ctx.paths.get("cost_mvp"), {})
        sem_max = cost.get("metrics", {}).get("semanas", {}).get("max", 99)
        if sem_plan > sem_max * 1.5:
            issues.append({"error": "plan excede cost_mvp.semanas_max × 1.5"})

        ok = len(issues) == 0
        result = {"ok": ok, "passed": passed, "issues": issues}
        save_json(ctx.paths["qc"], result)
        # QC informa issues pero no bloquea el pipeline
        return AgentResult(ok=True, data=result, artifacts=[str(ctx.paths["qc"])], warnings=[i.get("error", "") for i in issues])

"""Agente 13 — Improvement."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import LOGS_DIR, load_json, save_json
from src.types import AgentResult, PipelineContext


class ImprovementAgent:
    key = "improvement"

    def run(self, ctx: PipelineContext) -> AgentResult:
        qc = load_json(ctx.paths.get("qc"), {})
        verdict = load_json(ctx.paths["synthesis"], {})
        feedback = load_json(ctx.paths["meta_dir"] / "feedback.json", {})

        propuestas = []
        if not qc.get("ok"):
            propuestas.append({"tipo": "qc_fix", "detalle": "Revisar issues en qc_result.json", "prioridad": "alta"})

        if ctx.mock_web:
            propuestas.append({"tipo": "fuentes", "detalle": "Activar MOCK_WEB=false para trend/market/competition real", "prioridad": "media"})

        fb = feedback.get("resultado_real")
        if fb == "fracaso" and verdict.get("veredicto") == "viable":
            propuestas.append({"tipo": "pesos", "detalle": "Bajar confidence financial/scalability en weights.json", "campo": "financial", "delta": -0.05})
        if fb == "exito" and verdict.get("veredicto") == "condicional":
            propuestas.append({"tipo": "pesos", "detalle": "Subir confidence áreas subestimadas", "delta": +0.05})

        mejoras_path = LOGS_DIR / "mejoras.json"
        log = load_json(mejoras_path, []) or []
        entry = {"slug": ctx.slug, "at": datetime.now(timezone.utc).isoformat(), "propuestas": propuestas}
        log.append(entry)
        save_json(mejoras_path, log[-50:])

        prop_path = ctx.paths["meta_dir"] / "mejoras_propuestas.json"
        save_json(prop_path, {"propuestas": propuestas, "slug": ctx.slug})

        return AgentResult(ok=True, data=entry, artifacts=[str(prop_path)], notes=f"{len(propuestas)} propuestas")

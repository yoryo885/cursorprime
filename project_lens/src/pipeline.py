"""Orquestador — Project Lens (13 agentes)."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.competition_agent import CompetitionAgent
from src.agents.context_agent import ContextAgent
from src.agents.cost_mvp_agent import CostToMvpAgent
from src.agents.financial_agent import FinancialAgent
from src.agents.improvement_agent import ImprovementAgent
from src.agents.market_agent import MarketResearchAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.qc_agent import QCAgent
from src.agents.report_agent import ReportAgent
from src.agents.risk_agent import RiskAgent
from src.agents.scalability_agent import ScalabilityAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.trend_agent import TrendAgent
from src.config import (
    AGENT_FILES,
    LOGS_DIR,
    agents_for_modo,
    constitution_path,
    load_json,
    save_json,
    slug_dir,
    slug_meta,
    slug_output,
    weights_path,
)
from src.types import AgentResult, PipelineContext

AGENTS = {
    "context": ContextAgent(),
    "trend": TrendAgent(),
    "market": MarketResearchAgent(),
    "competition": CompetitionAgent(),
    "financial": FinancialAgent(),
    "scalability": ScalabilityAgent(),
    "cost_mvp": CostToMvpAgent(),
    "risk": RiskAgent(),
    "synthesis": SynthesisAgent(),
    "planner": PlannerAgent(),
    "qc": QCAgent(),
    "report": ReportAgent(),
    "improvement": ImprovementAgent(),
}


def build_context(slug: str, idea: dict, modo: str = "full", mock_web: bool = True) -> PipelineContext:
    meta = slug_meta(slug)
    paths = {"meta_dir": meta, "output": slug_output(slug), "lote": slug_dir(slug) / "inputs" / "idea.json"}
    for key, fname in AGENT_FILES.items():
        paths[key] = meta / fname
    return PipelineContext(
        slug=slug,
        paths=paths,
        idea=idea,
        constitution=load_json(constitution_path(), {}),
        weights=load_json(weights_path(), {}),
        modo=modo,
        mock_web=mock_web,
    )


def log_error(slug: str, step: str, error: str) -> None:
    p = LOGS_DIR / "errores.json"
    entries = load_json(p, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(p, entries)


def run_pipeline(slug: str, idea: dict, modo: str = "full", mock_web: bool = True, solo: str | None = None) -> bool:
    ctx = build_context(slug, idea, modo, mock_web)
    steps = [solo] if solo else agents_for_modo(modo)

    for step in steps:
        agent = AGENTS.get(step)
        if not agent:
            log_error(slug, step, "agente desconocido")
            return False
        print(f"  → {step}")
        try:
            result: AgentResult = agent.run(ctx)
        except Exception as exc:
            log_error(slug, step, f"{exc}\n{traceback.format_exc()}")
            return False
        if not result.ok and step == "qc":
            print(f"      ⚠ QC issues — continúa report")
        elif not result.ok:
            log_error(slug, step, result.notes)
            return False
        for w in result.warnings:
            print(f"      ⚠ {w}")
    return True

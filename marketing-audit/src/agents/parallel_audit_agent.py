"""Orquestador: lanza 5 agentes de dimensión en paralelo."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agents.competitive_agent import CompetitiveAgent
from src.agents.content_agent import ContentAgent
from src.agents.conversion_agent import ConversionAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.technical_agent import TechnicalAgent
from src.config import agents_meta, load_json
from src.types import AgentResult, PipelineContext

DIMENSION_AGENTS = [
    ContentAgent(),
    ConversionAgent(),
    CompetitiveAgent(),
    TechnicalAgent(),
    StrategyAgent(),
]


class ParallelAuditAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        discovery_path = ctx.paths["discovery"]
        if not discovery_path.exists():
            return AgentResult(ok=False, notes="Falta discovery.json")

        agents_dir = agents_meta(ctx.slug)
        agents_dir.mkdir(parents=True, exist_ok=True)

        def _run_one(agent):
            out = agents_dir / f"{agent.dimension}.json"
            agent.run_file(discovery_path, out)
            return agent.dimension, out

        completed: list[str] = []
        errors: list[str] = []

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(_run_one, a): a.dimension for a in DIMENSION_AGENTS}
            for fut in as_completed(futures):
                dim = futures[fut]
                try:
                    name, path = fut.result()
                    completed.append(name)
                except Exception as exc:
                    errors.append(f"{dim}: {exc}")

        if len(completed) < 3:
            return AgentResult(ok=False, notes=f"Fallaron agentes: {errors}")

        from src.config import save_json

        save_json(
            agents_dir / "manifest.json",
            {
                "parallel": True,
                "agents": completed,
                "errors": errors,
            },
        )

        return AgentResult(
            ok=True,
            artifacts=[str(agents_dir / "manifest.json")],
            notes=f"5 agentes paralelos — OK: {len(completed)}/5",
            warnings=errors,
        )

"""Orquestador del meta-creador."""

from __future__ import annotations

from src.agents.architecture_agent import ArchitectureAgent
from src.agents.brief_agent import BriefAgent
from src.agents.feasibility_agent import FeasibilityAgent
from src.agents.packager_agent import SpecPackagerAgent
from src.agents.qc_agent import ProjectQCAgent
from src.agents.research_agent import ResearchAgent
from src.agents.scaffold_agent import ScaffoldAgent
from src.checkpoint import Checkpoint
from src.config import PLAN_PATH, borrador_dir, load_json, proyecto_dir, slugify
from src.models import PipelineContext

AGENTS = {
    "BriefAgent": BriefAgent(),
    "ResearchAgent": ResearchAgent(),
    "ArchitectureAgent": ArchitectureAgent(),
    "FeasibilityAgent": FeasibilityAgent(),
    "ScaffoldAgent": ScaffoldAgent(),
    "SpecPackagerAgent": SpecPackagerAgent(),
    "ProjectQCAgent": ProjectQCAgent(),
}


class CreatorPipeline:
    def __init__(self, autorizado_construir: bool = False):
        self.plan = load_json(PLAN_PATH, {})
        self.autorizado_construir = autorizado_construir

    def run_diseno(self, slug: str, idea: dict) -> None:
        ctx = self._ctx(slug, idea)
        cp = Checkpoint.load(slug)
        cp.fase = "diseno"
        cp.save()

        for step in self.plan.get("pipeline", []):
            if step.get("fase") != "diseno":
                continue
            if step["id"] <= cp.last_completed_step:
                continue
            self._run_step(step, ctx, cp)

        print(f"\n✅ Diseño listo: borradores/{slug}/")
        print(f"   Lee: borradores/{slug}/DISEÑO.md")
        print(f"   Cuando estés listo: python main.py construir {slug}")

    def run_construccion(self, slug: str) -> None:
        if not self.autorizado_construir:
            raise PermissionError(
                "Construcción requiere: python main.py construir {slug}"
            )

        idea = load_json(borrador_dir(slug) / "meta" / "brief.json", {})
        if not idea:
            raise FileNotFoundError(f"No hay borrador para {slug}. Ejecuta diseñar primero.")

        ctx = self._ctx(slug, idea)
        ctx.autorizado_construir = True
        cp = Checkpoint.load(slug)
        cp.fase = "construccion"
        cp.save()

        for step in self.plan.get("pipeline", []):
            if step.get("fase") != "construccion":
                continue
            self._run_step(step, ctx, cp)

        print(f"\n✅ Proyecto construido: proyectos/{slug}/")
        print(f"   Lee: proyectos/{slug}/ENTREGA.txt")

    def _ctx(self, slug: str, idea: dict) -> PipelineContext:
        slug = slug or slugify(str(idea.get("titulo") or "proyecto"))
        return PipelineContext(
            slug=slug,
            borrador_dir=borrador_dir(slug),
            proyecto_dir=proyecto_dir(slug),
            idea=idea,
            autorizado_construir=self.autorizado_construir,
        )

    def _run_step(self, step: dict, ctx: PipelineContext, cp: Checkpoint) -> None:
        agent_name = step.get("agente", "")
        agent = AGENTS.get(agent_name)
        if not agent:
            raise ValueError(f"Agente desconocido: {agent_name}")

        print(f"  → [{step['id']}] {step.get('nombre')} ({agent_name})")
        result = agent.run(ctx)
        if not result.ok:
            raise RuntimeError(f"Paso {step['slug']} falló: {result.notes}")
        cp.mark_completed(step["id"], step["slug"], result.notes)

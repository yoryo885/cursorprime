"""Agente 5: genera repo en proyectos/ — SOLO con autorización."""

from __future__ import annotations

from pathlib import Path

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class ScaffoldAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        if not ctx.autorizado_construir:
            raise PermissionError(
                "Construcción bloqueada. Di: construye / armado / crea el proyecto"
            )

        plan = load_json(ctx.borrador_dir / "meta" / "plan.json", {})
        brief = load_json(ctx.borrador_dir / "meta" / "brief.json", {})
        slug = ctx.slug
        root = ctx.proyecto_dir

        if root.exists() and any(root.iterdir()):
            raise FileExistsError(
                f"proyectos/{slug}/ ya existe. Confirma sobrescritura antes de continuar."
            )

        root.mkdir(parents=True, exist_ok=True)
        (root / "src" / "agents").mkdir(parents=True, exist_ok=True)
        (root / "data" / slug / "meta").mkdir(parents=True, exist_ok=True)
        (root / "data" / slug / "inputs").mkdir(parents=True, exist_ok=True)
        (root / "data" / slug / "output").mkdir(parents=True, exist_ok=True)
        (root / "meta").mkdir(parents=True, exist_ok=True)
        (root / "logs").mkdir(parents=True, exist_ok=True)

        save_json(root / "meta" / "plan.json", plan)
        save_json(
            root / "meta" / "constitution.json",
            {
                "version": 1,
                "reglas": brief.get("restricciones") or {},
                "origen_borrador": str(ctx.borrador_dir),
            },
        )

        main_py = self._main_py(slug)
        (root / f"{slug}_main.py").write_text(main_py, encoding="utf-8")
        (root / "requirements.txt").write_text(
            "python-dotenv>=1.0.0\nplaywright>=1.40.0\n",
            encoding="utf-8",
        )
        (root / ".env.example").write_text(
            "# ANTHROPIC_API_KEY=\nMOCK_EXTERNAL=true\n",
            encoding="utf-8",
        )
        (root / "PROYECTO.md").write_text(
            self._proyecto_md(brief, slug),
            encoding="utf-8",
        )

        for step in plan.get("pipeline") or []:
            agente = step.get("agente", "StubAgent")
            agent_path = root / "src" / "agents" / f"{self._agent_file(agente)}"
            if not agent_path.exists():
                agent_path.write_text(self._agent_stub(agente, step), encoding="utf-8")

        (root / "src" / "pipeline.py").write_text(self._pipeline_stub(slug), encoding="utf-8")
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "agents" / "__init__.py").write_text("", encoding="utf-8")

        return AgentResult(ok=True, artifacts=[str(root)], notes=f"Scaffold en proyectos/{slug}/")

    @staticmethod
    def _agent_file(name: str) -> str:
        base = name.replace("Agent", "").lower()
        return f"{base}_agent.py"

    @staticmethod
    def _agent_stub(name: str, step: dict) -> str:
        return f'''"""{step.get("nombre", name)} — stub generado."""

class {name}:
    def run(self, ctx):
        # TODO: implementar {step.get("slug")}
        return {{"ok": True, "artifacts": [], "notes": "stub"}}
'''

    @staticmethod
    def _pipeline_stub(slug: str) -> str:
        return f'''"""Orquestador — generado desde ideas-de-proyectos."""

def run_pipeline(args):
    print("Pipeline {slug} — implementar pasos desde meta/plan.json")
'''

    @staticmethod
    def _main_py(slug: str) -> str:
        return f'''#!/usr/bin/env python3
"""CLI — {slug}"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Pipeline {slug}")
    parser.add_argument("--slug", default="{slug}")
    args = parser.parse_args()
    from src.pipeline import run_pipeline
    run_pipeline(args)


if __name__ == "__main__":
    main()
'''

    @staticmethod
    def _proyecto_md(brief: dict, slug: str) -> str:
        return f"""# {brief.get("nombre", slug)}

Generado desde **ideas de proyectos** (`borradores/{slug}/`).

## Comando

```bash
python {slug}_main.py --help
```

## Problema

{brief.get("problema", "")}

## Pendiente

Implementar agentes en `src/agents/` según `meta/plan.json`.
"""

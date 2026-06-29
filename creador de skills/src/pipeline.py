"""Orquestador — Creador de Skills."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.compose_agent import ComposeAgent
from src.agents.context_agent import ContextAgent
from src.agents.packager_agent import PackagerAgent
from src.agents.qc_agent import QcAgent
from src.agents.template_agent import TemplateAgent
from src.checkpoint import Checkpoint
from src.config import constitution_path, load_json, save_json, slug_dir, slug_meta, slug_output
from src.types import AgentResult, PipelineContext

STEPS = [
    ("Context", ContextAgent()),
    ("Template", TemplateAgent()),
    ("Compose", ComposeAgent()),
    ("QC", QcAgent()),
    ("Packager", PackagerAgent()),
]


def build_context(slug: str, solicitud: dict | None = None) -> PipelineContext:
    base = slug_dir(slug)
    meta = slug_meta(slug)
    output = slug_output(slug)
    return PipelineContext(
        slug=slug,
        paths={
            "solicitud": base / "inputs" / "solicitud.json",
            "meta": meta,
            "context": meta / "context.json",
            "plantilla": meta / "plantilla.json",
            "composed": meta / "composed.json",
            "qc": meta / "qc_result.json",
            "skill_md": output / "SKILL.md",
            "reference_md": output / "reference.md",
            "output": output,
        },
        solicitud=solicitud or {},
        constitution=load_json(constitution_path(), {}),
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def _run_agent(label: str, agent, ctx: PipelineContext) -> bool:
    print(f"  → {label}")
    try:
        result: AgentResult = agent.run(ctx)
    except Exception as exc:
        log_error(ctx.slug, label, f"{exc}\n{traceback.format_exc()}")
        return False
    if not result.ok:
        log_error(ctx.slug, label, str(result.notes))
        print(f"      ✗ {result.notes}")
        return False
    return True


def run_pipeline(slug: str, solicitud: dict | None = None, reset: bool = False) -> bool:
    if reset:
        Checkpoint.load(slug).reset()
    ctx = build_context(slug, solicitud)
    for label, agent in STEPS:
        if not _run_agent(label, agent, ctx):
            return False
    return True

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.assembler_agent import AssemblerAgent
from src.agents.context_agent import ContextAgent
from src.agents.copy_agent import CopyAgent
from src.agents.qc_agent import QCAgent
from src.agents.visual_agent import VisualAgent
from src.checkpoint import Checkpoint
from src.config import ROOT, load_json, save_json, slug_dir, slug_meta, slug_output
from src.types import AgentResult, PipelineContext

STEPS = [
    ("context", ContextAgent()),
    ("visual", VisualAgent()),
    ("copy", CopyAgent()),
    ("qc", QCAgent()),
    ("assemble", AssemblerAgent()),
]


def build_context(slug: str, producto: str, mock: bool = True) -> PipelineContext:
    base = slug_dir(slug)
    return PipelineContext(
        slug=slug,
        producto=producto,
        mock=mock,
        paths={
            "marca": base / "inputs" / "marca.json",
            "meta": slug_meta(slug),
            "output": slug_output(slug),
        },
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = ROOT / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def run_pipeline(
    slug: str,
    producto: str = "pareto",
    mock: bool = True,
    reset: bool = False,
    solo: str | None = None,
) -> bool:
    if reset:
        Checkpoint.load(slug).reset()

    ctx = build_context(slug, producto, mock=mock)
    cp = Checkpoint.load(slug)

    for step_id, agent in STEPS:
        if solo and step_id != solo:
            continue
        if cp.is_done(step_id) and not reset and not solo:
            print(f"  ⏭ {step_id} (checkpoint)")
            _hydrate(ctx, step_id)
            continue
        print(f"  → {step_id}")
        try:
            result: AgentResult = agent.run(ctx)
        except Exception as exc:
            log_error(slug, step_id, f"{exc}\n{traceback.format_exc()}")
            print(f"      ✗ {exc}")
            return False
        if not result.ok:
            log_error(slug, step_id, result.notes)
            print(f"      ✗ {result.notes}")
            return False
        for w in result.warnings:
            print(f"      ⚠ {w}")
        cp.mark(step_id)

    return True


def _hydrate(ctx: PipelineContext, step_id: str) -> None:
    meta = slug_meta(ctx.slug)
    if step_id in ("visual", "copy", "qc", "assemble"):
        ctx.marca = load_json(ctx.paths["marca"], {}) or {}
        from src.config import kdp_listing_path
        ctx.kdp = load_json(kdp_listing_path(ctx.producto), {}) or {}
    if step_id in ("copy", "qc", "assemble"):
        assets_data = load_json(meta / "assets.json", {}) or {}
        ctx.assets = assets_data.get("files", assets_data)
    if step_id in ("qc", "assemble"):
        from src.agents.copy_agent import CopyAgent
        CopyAgent().run(ctx)

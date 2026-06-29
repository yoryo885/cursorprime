"""Pipeline 1 — Investigación (YouTube + web → análisis)."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.context_investigacion_agent import ContextInvestigacionAgent
from src.agents.fetch_agent import FetchAgent
from src.agents.packager_investigacion_agent import PackagerInvestigacionAgent
from src.agents.qc_investigacion_agent import QcInvestigacionAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.checkpoint import Checkpoint
from src.config import constitution_path, load_json, save_json, slug_dir, slug_meta, slug_output
from src.types import AgentResult, PipelineContext

STEPS = [
    ("Context", ContextInvestigacionAgent()),
    ("Fetch", FetchAgent()),
    ("Synthesis", SynthesisAgent()),
    ("QC", QcInvestigacionAgent()),
    ("Packager", PackagerInvestigacionAgent()),
]


def build_context(slug: str, brief: dict | None = None) -> PipelineContext:
    base = slug_dir(slug)
    meta = slug_meta(slug)
    return PipelineContext(
        slug=slug,
        paths={
            "brief": base / "inputs" / "brief.json",
            "meta": meta,
            "context": meta / "context.json",
            "fetch": meta / "fetch.json",
            "analisis": meta / "analisis.json",
            "qc": meta / "qc_result.json",
            "output": slug_output(slug),
        },
        brief=brief or {},
        constitution=load_json(constitution_path(), {}),
        modo="investigacion",
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def run_investigacion(slug: str, brief: dict | None = None, reset: bool = False) -> bool:
    if brief:
        dest = slug_dir(slug) / "inputs" / "brief.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        save_json(dest, brief)

    ctx = build_context(slug, brief)
    cp = Checkpoint(slug)
    if reset:
        cp.reset()

    print(f"\n🔍 Investigación — {slug}\n")
    for label, agent in STEPS:
        if cp.is_done(label):
            print(f"  ⏭ {label} (checkpoint)")
            continue
        print(f"  → {label}")
        try:
            result: AgentResult = agent.run(ctx)
        except Exception as exc:
            log_error(slug, label, f"{exc}\n{traceback.format_exc()}")
            print(f"  ✗ Error en {label}")
            return False
        if not result.ok:
            log_error(slug, label, result.notes or "falló")
            print(f"  ✗ {label}: {result.notes}")
            return False
        cp.mark(label)
        if result.notes:
            print(f"     {result.notes}")

    print(f"\n✅ Análisis: data/{slug}/output/analisis.md\n")
    return True

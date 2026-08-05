"""Orquestador — Creador de Landings."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.brief_agent import BriefAgent
from src.agents.build_agent import BuildAgent
from src.agents.examples_agent import ExamplesAgent
from src.agents.interview_agent import InterviewAgent
from src.agents.packager_agent import PackagerAgent
from src.agents.qc_agent import QcAgent
from src.checkpoint import Checkpoint
from src.config import (
    constitution_path,
    load_json,
    save_json,
    slug_dir,
    slug_inputs,
    slug_meta,
    slug_output,
)
from src.types import AgentResult, PipelineContext

STEPS = [
    ("Interview", "interview", InterviewAgent()),
    ("Examples", "examples", ExamplesAgent()),
    ("Brief", "brief", BriefAgent()),
    ("Build", "build", BuildAgent()),
    ("QC", "qc", QcAgent()),
    ("Packager", "packager", PackagerAgent()),
]


def build_context(slug: str, respuestas: dict | None = None, ejemplo: str = "") -> PipelineContext:
    meta = slug_meta(slug)
    out = slug_output(slug)
    inp = slug_inputs(slug)
    for d in (meta, out, inp):
        d.mkdir(parents=True, exist_ok=True)
    resp = respuestas or load_json(inp / "respuestas.json", {}) or {}
    if ejemplo:
        resp["ejemplo_elegido"] = ejemplo
    return PipelineContext(
        slug=slug,
        paths={
            "root": slug_dir(slug),
            "respuestas": inp / "respuestas.json",
            "meta": meta,
            "output": out,
            "brief": meta / "brief.json",
            "preview": out / "preview.html",
            "qc": meta / "qc_result.json",
        },
        respuestas=resp,
        constitution=load_json(constitution_path(), {}) or {},
        ejemplo=resp.get("ejemplo_elegido") or ejemplo or "editorial",
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    if not isinstance(entries, list):
        entries = []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def run_pipeline(
    slug: str,
    respuestas: dict | None = None,
    ejemplo: str = "",
    reset: bool = False,
    solo: str | None = None,
) -> bool:
    if reset:
        Checkpoint.load(slug).reset()

    ctx = build_context(slug, respuestas=respuestas, ejemplo=ejemplo)
    cp = Checkpoint.load(slug)

    for label, step_id, agent in STEPS:
        if solo and solo != step_id:
            continue
        if not solo and cp.is_done(step_id):
            print(f"  · {label} (skip)")
            continue
        print(f"  → {label}")
        try:
            result: AgentResult = agent.run(ctx)
        except Exception as exc:
            log_error(slug, label, f"{exc}\n{traceback.format_exc()}")
            print(f"      ✗ {exc}")
            return False
        if not result.ok:
            log_error(slug, label, result.notes)
            print(f"      ✗ {result.notes}")
            return False
        if not solo:
            cp.mark(step_id)
    return True

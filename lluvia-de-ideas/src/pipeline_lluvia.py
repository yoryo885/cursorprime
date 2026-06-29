"""Pipeline 2 — Lluvia de ideas (análisis + dirección → cola pendiente)."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.context_lluvia_agent import ContextLluviaAgent
from src.agents.idea_generator_agent import IdeaGeneratorAgent
from src.agents.packager_lluvia_agent import PackagerLluviaAgent
from src.agents.qc_lluvia_agent import QcLluviaAgent
from src.checkpoint import Checkpoint
from src.config import constitution_path, analisis_json_path, load_json, save_json, slug_dir, slug_meta, slug_output
from src.types import AgentResult, PipelineContext

STEPS = [
    ("Context", ContextLluviaAgent()),
    ("Ideas", IdeaGeneratorAgent()),
    ("QC", QcLluviaAgent()),
    ("Packager", PackagerLluviaAgent()),
]


def build_context(slug: str, brief: dict | None = None, analisis_slug: str | None = None) -> PipelineContext:
    base = slug_dir(slug)
    meta = slug_meta(slug)
    a_slug = analisis_slug or (brief or {}).get("analisis_slug") or slug.replace("lluvia_", "").replace("lluvia-", "")
    analisis_path = analisis_json_path(a_slug)

    return PipelineContext(
        slug=slug,
        paths={
            "brief": base / "inputs" / "brief.json",
            "meta": meta,
            "context": meta / "context.json",
            "analisis": analisis_path,
            "ideas": meta / "ideas.json",
            "qc": meta / "qc_result.json",
            "output": slug_output(slug),
        },
        brief={**(brief or {}), "analisis_slug": a_slug},
        constitution=load_json(constitution_path(), {}),
        modo="lluvia",
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def run_lluvia(
    slug: str,
    brief: dict | None = None,
    analisis_slug: str | None = None,
    reset: bool = False,
) -> bool:
    if brief:
        dest = slug_dir(slug) / "inputs" / "brief.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        save_json(dest, brief)

    ctx = build_context(slug, brief, analisis_slug)
    cp = Checkpoint(slug)
    if reset:
        cp.reset()

    print(f"\n🌧 Lluvia de ideas — {slug}\n")
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

    print(f"\n✅ Ideas en cola/pendientes/ — revisa con: cola listar\n")
    return True

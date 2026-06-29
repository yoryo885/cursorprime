"""Pipeline — URL → 5 agentes paralelos → MARKETING-AUDIT.md."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.context_agent import ContextAgent
from src.agents.discovery_agent import DiscoveryAgent
from src.agents.packager_agent import PackagerAgent
from src.agents.parallel_audit_agent import ParallelAuditAgent
from src.agents.pdf_agent import PdfAgent
from src.agents.qc_agent import QcAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.checkpoint import Checkpoint
from src.config import agents_meta, constitution_path, load_json, save_json, slug_dir, slug_meta, slug_output
from src.types import AgentResult, PipelineContext

STEPS = [
    ("Context", ContextAgent()),
    ("Discovery", DiscoveryAgent()),
    ("ParallelAudit", ParallelAuditAgent()),
    ("Synthesis", SynthesisAgent()),
    ("QC", QcAgent()),
    ("Packager", PackagerAgent()),
    ("PDF", PdfAgent()),
]


def build_context(slug: str, brief: dict | None = None, flags: dict | None = None) -> PipelineContext:
    base = slug_dir(slug)
    meta = slug_meta(slug)
    return PipelineContext(
        slug=slug,
        paths={
            "brief": base / "inputs" / "brief.json",
            "meta": meta,
            "context": meta / "context.json",
            "discovery": meta / "discovery.json",
            "synthesis": meta / "synthesis.json",
            "qc": meta / "qc_result.json",
            "output": slug_output(slug),
            "agents": agents_meta(slug),
        },
        brief=brief or {},
        constitution=load_json(constitution_path(), {}),
        flags=flags or {},
    )


def log_error(slug: str, step: str, error: str) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / "errores.json"
    entries = load_json(log_path, []) or []
    entries.append({"slug": slug, "step": step, "error": error, "at": datetime.now(timezone.utc).isoformat()})
    save_json(log_path, entries)


def run_audit(
    slug: str,
    brief: dict | None = None,
    reset: bool = False,
    pdf: bool = False,
    skip_pdf: bool = False,
) -> bool:
    if brief:
        dest = slug_dir(slug) / "inputs" / "brief.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        save_json(dest, brief)

    flags = {"pdf": pdf and not skip_pdf}
    ctx = build_context(slug, brief, flags)
    cp = Checkpoint(slug)
    if reset:
        cp.reset()

    print(f"\n📊 Marketing Audit — {slug}\n")
    for label, agent in STEPS:
        if label == "PDF" and not flags.get("pdf"):
            continue
        if cp.is_done(label):
            print(f"  ⏭ {label} (checkpoint)")
            continue
        print(f"  → {label}")
        try:
            result: AgentResult = agent.run(ctx)
        except Exception as exc:
            log_error(slug, label, f"{exc}\n{traceback.format_exc()}")
            print(f"  ✗ Error en {label}: {exc}")
            return False
        if not result.ok:
            if label == "PDF":
                print(f"  ⚠ PDF: {result.notes}")
                continue
            log_error(slug, label, result.notes or "falló")
            print(f"  ✗ {label}: {result.notes}")
            return False
        cp.mark(label)
        if result.notes:
            print(f"     {result.notes}")
        for w in result.warnings:
            print(f"     ⚠ {w}")

    print(f"\n✅ Audit: data/{slug}/output/MARKETING-AUDIT.md\n")
    return True

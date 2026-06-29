"""Orquestador — Creador de Contenido."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.agents.context_agent import ContextAgent
from src.agents.escenas_agent import EscenasAgent
from src.agents.packager_agent import PackagerAgent
from src.agents.prompt_agent import PromptAgent
from src.agents.qc_agent import QcAgent
from src.agents.style_agent import StyleAgent
from src.checkpoint import Checkpoint
from src.config import (
    MOCK_GENERATE,
    constitution_path,
    load_json,
    normalizar_salidas,
    plan_path,
    salidas_con_dependencias,
    save_json,
    slug_dir,
    slug_gifs,
    slug_imagenes,
    slug_meta,
    slug_output,
    slug_pdf,
    slug_clips,
    slug_videos,
)
from gifs.agent import GifsModule
from imagenes.agent import ImagenesModule
from pdf.agent import PdfModule
from videos.agent import VideosModule
from src.types import AgentResult, PipelineContext

CORE = {
    "context": ContextAgent(),
    "style": StyleAgent(),
    "prompt": PromptAgent(),
}

MODULOS = {
    "png": ("imagenes", ImagenesModule()),
    "gif": ("gifs", GifsModule()),
    "video": ("videos", VideosModule()),
    "pdf": ("pdf", PdfModule()),
}


def build_context(slug: str, lote: dict | None = None, modo: str | None = None) -> PipelineContext:
    raw = lote or {}
    if modo and modo != "all":
        raw = {**raw, "salidas": [modo]}
    salidas = salidas_con_dependencias(normalizar_salidas(raw))

    base = slug_dir(slug)
    meta = slug_meta(slug)
    return PipelineContext(
        slug=slug,
        paths={
            "lote": base / "inputs" / "lote.json",
            "meta": meta,
            "context": meta / "context.json",
            "imagenes_out": slug_imagenes(slug),
            "gifs_out": slug_gifs(slug),
            "videos_out": slug_videos(slug),
            "pdf_out": slug_pdf(slug),
            "output": slug_output(slug),
            "escenas": meta / "escenas.json",
            "style": meta / "style.json",
            "prompts": meta / "prompts.json",
            "generated_imagenes": meta / "generated_imagenes.json",
            "generated_gifs": meta / "generated_gifs.json",
            "generated_videos": meta / "generated_videos.json",
            "generated_pdf": meta / "generated_pdf.json",
            "qc": meta / "qc_result.json",
        },
        lote=raw,
        constitution=load_json(constitution_path(), {}),
        salidas=salidas,
        mock_generate=MOCK_GENERATE,
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
        log_error(ctx.slug, label, result.notes)
        return False
    for w in result.warnings:
        print(f"      ⚠ {w}")
    return True


def run_pipeline(
    slug: str,
    lote: dict | None = None,
    modo: str = "all",
    reset: bool = False,
) -> bool:
    if reset:
        Checkpoint.load(slug).reset()

    ctx = build_context(slug, lote, modo=None if modo == "all" else modo)
    context_agent = CORE["context"]
    if not _run_agent("Core · Context", context_agent, ctx):
        return False

    ctx = build_context(slug, load_json(ctx.paths["lote"], {}) or lote)
    ctx.salidas = load_json(ctx.paths["context"], {}).get("salidas_efectivas", ctx.salidas)
    context_data = load_json(ctx.paths["context"], {})

    video_cfg = context_data.get("video") or {}
    raw_lote = load_json(ctx.paths["lote"], {}) or lote or {}
    needs_escenas = (
        "video" in ctx.salidas
        and video_cfg.get("modo") == "animado"
        and (raw_lote.get("guion") or raw_lote.get("escenas"))
    )
    if needs_escenas and not _run_agent("Core · Escenas", EscenasAgent(), ctx):
        return False

    for name, agent in [("Style", CORE["style"]), ("Prompt", CORE["prompt"])]:
        if not _run_agent(f"Core · {name}", agent, ctx):
            return False

    salidas = ctx.salidas
    orden_modulos = [s for s in ("png", "gif", "video", "pdf") if s in salidas]

    for salida in orden_modulos:
        label, module = MODULOS[salida]
        if not _run_agent(f"Módulo · {label}", module, ctx):
            return False

    if not _run_agent("Core · QC", QcAgent(), ctx):
        return False
    if not _run_agent("Core · Packager", PackagerAgent(), ctx):
        return False

    return True

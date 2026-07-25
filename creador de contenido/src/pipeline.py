"""Orquestador — Creador de Contenido (recetas + agentes condicionales)."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path

from gifs.agent import GifsModule
from imagenes.agent import ImagenesModule
from pdf.agent import PdfModule
from src.agents.captions_agent import CaptionsAgent
from src.agents.context_agent import ContextAgent
from src.agents.escenas_agent import EscenasAgent
from src.agents.guion_agent import GuionAgent
from src.agents.hook_agent import HookAgent
from src.agents.packager_agent import PackagerAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.prompt_agent import PromptAgent
from src.agents.qc_agent import QcAgent
from src.agents.style_agent import StyleAgent
from src.agents.thumbnail_agent import ThumbnailAgent
from src.checkpoint import Checkpoint
from src.config import (
    MOCK_GENERATE,
    constitution_path,
    load_json,
    save_json,
    slug_clips,
    slug_dir,
    slug_gifs,
    slug_imagenes,
    slug_meta,
    slug_output,
    slug_pdf,
    slug_videos,
)
from src.recipes import AGENT_ORDER, MODULO_STEPS, resolve_recipe
from src.types import AgentResult, PipelineContext
from videos.agent import VideosModule

AGENTS = {
    "context": ContextAgent(),
    "planner": PlannerAgent(),
    "hook": HookAgent(),
    "guion": GuionAgent(),
    "escenas": EscenasAgent(),
    "style": StyleAgent(),
    "prompt": PromptAgent(),
    "png": ImagenesModule(),
    "gif": GifsModule(),
    "video": VideosModule(),
    "pdf": PdfModule(),
    "captions": CaptionsAgent(),
    "thumbnail": ThumbnailAgent(),
    "qc": QcAgent(),
    "packager": PackagerAgent(),
}

LABELS = {
    "context": "Core · Context",
    "planner": "Core · Planner",
    "hook": "Copy · Hook (hooks-redes)",
    "guion": "Copy · Guion",
    "escenas": "Core · Escenas",
    "style": "Core · Style",
    "prompt": "Core · Prompt",
    "png": "Módulo · imagenes",
    "gif": "Módulo · gifs",
    "video": "Módulo · videos",
    "pdf": "Módulo · pdf",
    "captions": "Copy · Captions (captions-redes)",
    "thumbnail": "Copy · Thumbnail (thumbnail-social)",
    "qc": "Core · QC",
    "packager": "Core · Packager",
}


def build_context(
    slug: str,
    lote: dict | None = None,
    modo: str | None = None,
    receta: str | None = None,
) -> PipelineContext:
    raw = dict(lote or {})
    if modo and modo != "all":
        raw = {**raw, "salidas": [modo]}
    if receta:
        raw = {**raw, "receta": receta}

    plan_preview = resolve_recipe(raw, receta)
    salidas = plan_preview["salidas"]
    if modo and modo != "all":
        # CLI --modo acota salidas medias pero mantiene receta de copy si aplica
        from src.config import salidas_con_dependencias

        salidas = salidas_con_dependencias([modo])

    base = slug_dir(slug)
    meta = slug_meta(slug)
    copy_dir = base / "copy"
    return PipelineContext(
        slug=slug,
        paths={
            "lote": base / "inputs" / "lote.json",
            "meta": meta,
            "context": meta / "context.json",
            "plan_runtime": meta / "plan_runtime.json",
            "hooks": meta / "hooks.json",
            "guion": meta / "guion.json",
            "guion_md": copy_dir / "guion.md",
            "captions": meta / "captions.json",
            "thumbnail": meta / "thumbnail.json",
            "copy_dir": copy_dir,
            "imagenes_out": slug_imagenes(slug),
            "gifs_out": slug_gifs(slug),
            "videos_out": slug_videos(slug),
            "pdf_out": slug_pdf(slug),
            "clips_out": slug_clips(slug),
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
        receta=plan_preview["receta"],
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
    if result.notes:
        print(f"      {result.notes}")
    return True


def _steps_for_run(ctx: PipelineContext, solo: str | None = None) -> list[str]:
    if solo:
        return [solo]
    plan_path = ctx.paths.get("plan_runtime")
    if plan_path and plan_path.exists():
        plan = load_json(plan_path, {}) or {}
        steps = plan.get("agentes") or []
        if steps:
            return [s for s in steps if s in AGENTS]
    # Fallback: order from recipe
    plan = resolve_recipe(ctx.lote, ctx.receta)
    return [s for s in plan["agentes"] if s in AGENTS]


def run_pipeline(
    slug: str,
    lote: dict | None = None,
    modo: str = "all",
    reset: bool = False,
    receta: str | None = None,
    solo: str | None = None,
    desde: str | None = None,
) -> bool:
    if reset:
        Checkpoint.load(slug).reset()

    ctx = build_context(slug, lote, modo=None if modo == "all" else modo, receta=receta)

    # Context + planner siempre (baratos; aseguran meta/lote frescos)
    if not solo:
        if not _run_agent(LABELS["context"], AGENTS["context"], ctx):
            return False
        ctx = build_context(
            slug,
            load_json(ctx.paths["lote"], {}) or lote,
            modo=None if modo == "all" else modo,
            receta=receta or ctx.receta,
        )
        if not _run_agent(LABELS["planner"], AGENTS["planner"], ctx):
            return False
    else:
        # --solo: no reescribe plan; necesita contexto previo o lo regenera mínimo
        if not _run_agent(LABELS["context"], AGENTS["context"], ctx):
            return False
        ctx = build_context(
            slug,
            load_json(ctx.paths["lote"], {}) or lote,
            modo=None if modo == "all" else modo,
            receta=receta or ctx.receta,
        )

    steps = _steps_for_run(ctx, solo=solo)
    skip: set[str] = set()
    if not solo:
        skip.update({"context", "planner"})  # ya corridos arriba

    ckpt = Checkpoint.load(slug)

    # Reanudación: --desde o último slug del checkpoint
    resume_from = desde or (None if reset or solo else ckpt.last_completed_slug or None)
    if resume_from and resume_from in steps and not solo:
        idx = steps.index(resume_from)
        # Si viene del checkpoint (ya completado), saltar ese y los anteriores
        if not desde:
            skip.update(steps[: idx + 1])
            print(f"   ↩ Reanudando después de «{resume_from}» ({len(skip)} pasos en skip)")
        else:
            # --desde X: empezar EN X (no rehacer anteriores)
            skip.update(s for s in steps[:idx] if s not in {"context", "planner"})
            print(f"   ↩ Desde «{desde}»")

    for i, step in enumerate(steps, start=1):
        if step in skip:
            continue
        if step not in AGENTS:
            log_error(slug, step, "agente desconocido")
            return False
        if step in MODULO_STEPS and step not in ctx.salidas and modo != "all":
            continue
        label = LABELS.get(step, step)
        if not _run_agent(label, AGENTS[step], ctx):
            return False
        ckpt.mark_completed(i, step)

    return True

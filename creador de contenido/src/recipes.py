"""Recetas de video — resuelven qué agentes/skills/salidas activar."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import META_DIR, load_json, normalizar_salidas, salidas_con_dependencias

RECETAS_PATH = META_DIR / "recetas.json"

# Orden canónico de pasos del sistema de video
AGENT_ORDER = [
    "context",
    "planner",
    "hook",
    "guion",
    "escenas",
    "style",
    "prompt",
    "png",
    "gif",
    "video",
    "audio",
    "pdf",
    "captions",
    "thumbnail",
    "qc",
    "packager",
]

MODULO_STEPS = {"png", "gif", "video", "pdf"}
COPY_STEPS = {"hook", "guion", "captions", "thumbnail", "audio"}


def load_recetas() -> dict[str, Any]:
    data = load_json(RECETAS_PATH, {}) or {}
    return data.get("recetas") or {}


def infer_receta(lote: dict[str, Any]) -> str:
    """Si el lote no trae receta, infiere según contenido."""
    explicit = (lote.get("receta") or "").strip().lower()
    if explicit:
        return explicit
    if lote.get("guia") or lote.get("fuente_guia"):
        return "promo-guia"
    video = lote.get("video") or {}
    modo = (video.get("modo") or "").lower()
    salidas = set(normalizar_salidas(lote))
    copy_flags = set(lote.get("copy") or [])
    if copy_flags & {"hook", "captions", "thumbnail"} or lote.get("pack_redes"):
        return "reels-pack"
    if "video" in salidas and modo == "animado" and (lote.get("guion") or lote.get("escenas")):
        return "animado"
    if "video" in salidas:
        return "slideshow"
    return "custom"


def resolve_recipe(lote: dict[str, Any], receta_cli: str | None = None) -> dict[str, Any]:
    """Devuelve plan runtime: agentes, skills, salidas, video_modo, receta_id."""
    catalog = load_recetas()
    receta_id = (receta_cli or "").strip().lower() or infer_receta(lote)
    if receta_id not in catalog:
        receta_id = "custom"
    recipe = dict(catalog[receta_id])

    salidas_lote = normalizar_salidas(lote) if lote.get("salidas") else []
    salidas = list(recipe.get("salidas") or []) or salidas_lote or ["png"]
    if salidas_lote and receta_id == "custom":
        salidas = salidas_lote
    salidas = salidas_con_dependencias(salidas)

    video_modo = recipe.get("video_modo")
    video_cfg = dict(lote.get("video") or {})
    if video_modo:
        video_cfg["modo"] = video_modo
    elif not video_cfg.get("modo"):
        video_cfg["modo"] = "slideshow"

    agentes = list(recipe.get("agentes") or [])
    if receta_id == "custom" or not agentes:
        agentes = _agentes_desde_lote(lote, salidas, video_cfg)

    # Asegurar dependencias mínimas
    agentes = _ensure_core(agentes, salidas, video_cfg, lote)

    skills = list(recipe.get("skills") or [])
    copy_needed = list(recipe.get("copy") or [])
    for step in COPY_STEPS:
        if step in agentes and step not in copy_needed:
            copy_needed.append(step)

    return {
        "receta": receta_id,
        "nombre": recipe.get("nombre") or receta_id,
        "descripcion": recipe.get("descripcion") or "",
        "skills": skills,
        "agentes": [a for a in AGENT_ORDER if a in set(agentes)],
        "salidas": salidas,
        "video": video_cfg,
        "copy": copy_needed,
        "requiere": list(recipe.get("requiere") or []),
    }


def _agentes_desde_lote(lote: dict, salidas: list[str], video_cfg: dict) -> list[str]:
    steps = ["context", "planner", "style", "prompt"]
    copy = set(lote.get("copy") or [])
    if "hook" in copy or lote.get("hook"):
        steps.append("hook")
    needs_guion = (
        "guion" in copy
        or lote.get("guia")
        or lote.get("fuente_guia")
        or (video_cfg.get("modo") == "animado" and not lote.get("guion") and not lote.get("escenas"))
    )
    if needs_guion:
        steps.append("guion")
    if "video" in salidas and video_cfg.get("modo") == "animado":
        steps.append("escenas")
    for s in ("png", "gif", "video", "pdf"):
        if s in salidas:
            steps.append(s)
    if "captions" in copy:
        steps.append("captions")
    if "thumbnail" in copy:
        steps.append("thumbnail")
    steps.extend(["qc", "packager"])
    return steps


def _ensure_core(agentes: list[str], salidas: list[str], video_cfg: dict, lote: dict) -> list[str]:
    s = set(agentes)
    s.update(["context", "planner", "style", "prompt", "qc", "packager"])
    for m in ("png", "gif", "video", "pdf"):
        if m in salidas:
            s.add(m)
    if "video" in salidas and video_cfg.get("modo") == "animado":
        s.add("escenas")
        if not lote.get("guion") and not lote.get("escenas"):
            s.add("guion")
    return [a for a in AGENT_ORDER if a in s]


def validate_requirements(plan: dict[str, Any], lote: dict[str, Any]) -> list[str]:
    """Errores de requisitos de receta (no bloquea si hay datos equivalentes)."""
    errors = []
    requiere = set(plan.get("requiere") or [])
    if "guion" in requiere and not (lote.get("guion") or lote.get("escenas") or lote.get("guia")):
        errors.append("Receta requiere guion, escenas o guia en lote.json")
    if "guia" in requiere and not (lote.get("guia") or lote.get("fuente_guia") or lote.get("guion")):
        errors.append("Receta promo-guia requiere guia, fuente_guia o guion")
    return errors

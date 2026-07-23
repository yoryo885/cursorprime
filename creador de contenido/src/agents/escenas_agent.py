"""Divide guion en escenas (frame inicio + fin + animación)."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from src.config import load_json, save_json, slugify
from src.types import AgentResult, PipelineContext

MAX_ESCENAS_DEFAULT = 8


def _split_guion(guion: str, max_escenas: int) -> list[str]:
    """Heurística MVP: párrafos o frases → escenas."""
    guion = guion.strip()
    if not guion:
        return []
    partes = [p.strip() for p in re.split(r"\n\s*\n", guion) if p.strip()]
    if len(partes) == 1:
        frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", guion) if f.strip()]
        partes = frases or [guion]
    if len(partes) > max_escenas:
        chunk = max(1, len(partes) // max_escenas)
        merged = []
        for i in range(0, len(partes), chunk):
            merged.append(" ".join(partes[i : i + chunk]))
        partes = merged[:max_escenas]
    return partes[:max_escenas]


def _build_escena(i: int, texto: str, estilo: str) -> dict:
    slug = slugify(texto[:40]) or f"escena_{i}"
    return {
        "id": i,
        "titulo": texto[:80],
        "texto_guion": texto,
        "start_frame_prompt": (
            f"Start frame, {estilo} style, scene: {texto[:120]}, "
            "illustration, clean composition, no text, square"
        ),
        "end_frame_prompt": (
            f"End frame, same style and characters as start, {estilo}, "
            f"scene conclusion: {texto[:120]}, no text, square"
        ),
        "animation_prompt": (
            f"Smooth subtle motion from start to end, {estilo}, "
            f"expressive but professional, topic: {texto[:80]}"
        ),
        "slug": slug,
        "archivo_inicio": f"{i:02d}-{slug}-inicio.png",
        "archivo_fin": f"{i:02d}-{slug}-fin.png",
        "archivo_clip": f"{i:02d}-{slug}.mp4",
    }


class EscenasAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        raw = load_json(ctx.paths["lote"], {}) or ctx.lote
        video_cfg = context.get("video") or {}
        estilo = context.get("estilo", "yordy-minimal")
        limit = int(video_cfg.get("limit_escenas") or MAX_ESCENAS_DEFAULT)

        guion_meta = load_json(ctx.paths.get("guion"), {}) if ctx.paths.get("guion") else {}
        guion_texto = raw.get("guion") or (guion_meta or {}).get("guion") or context.get("guion") or ""

        if raw.get("escenas"):
            escenas = raw["escenas"][:limit]
        elif guion_texto:
            textos = _split_guion(str(guion_texto), limit)
            escenas = [_build_escena(i + 1, t, estilo) for i, t in enumerate(textos)]
        else:
            return AgentResult(ok=False, notes="Modo animado requiere guion, escenas o agente guion previo")

        out = ctx.paths["escenas"]
        payload = {
            "escenas": escenas,
            "count": len(escenas),
            "modo_video": "animado",
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out, payload)
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"{len(escenas)} escenas")

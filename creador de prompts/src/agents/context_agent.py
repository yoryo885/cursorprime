"""Agente 1: carga solicitud y resuelve proyecto destino."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, proyectos_registry_path, save_json
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        raw = load_json(ctx.paths["solicitud"], {}) or ctx.solicitud
        tipo = (raw.get("tipo") or "imagen").lower()
        destino_id = raw.get("proyecto_destino") or "general"

        registry = load_json(proyectos_registry_path(), {"proyectos": []})
        proyecto = next(
            (p for p in registry.get("proyectos", []) if p.get("id") == destino_id),
            None,
        )

        context = {
            "titulo": raw.get("titulo") or ctx.slug,
            "tipo": tipo,
            "proyecto_destino": destino_id,
            "proyecto_nombre": (proyecto or {}).get("nombre", "General"),
            "temas": raw.get("temas") or [raw.get("tema", "general")],
            "contexto": raw.get("contexto") or {},
            "variantes": int(raw.get("variantes") or 1),
            "notas": raw.get("notas", ""),
            "creado_at": datetime.now(timezone.utc).isoformat(),
        }

        save_json(ctx.paths["context"], context)
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["context"])],
            notes=f"{tipo} → {destino_id}",
        )

"""Agente 1: normaliza solicitud y resuelve proyecto."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, proyectos_registry_path, save_json, slugify
from src.types import AgentResult, PipelineContext


class ContextAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        raw = load_json(ctx.paths["solicitud"], {}) or ctx.solicitud
        nombre = slugify(raw.get("nombre") or raw.get("titulo") or ctx.slug)
        tipo = (raw.get("tipo") or "workflow").lower()
        destino_id = raw.get("proyecto_destino") or "general"
        triggers = raw.get("triggers") or []

        registry = load_json(proyectos_registry_path(), {"proyectos": []})
        proyecto = next((p for p in registry.get("proyectos", []) if p.get("id") == destino_id), {})

        context = {
            "nombre": nombre,
            "titulo": raw.get("titulo") or nombre,
            "tipo": tipo,
            "proyecto_destino": destino_id,
            "proyecto_nombre": proyecto.get("nombre", "General"),
            "proyecto_carpeta": proyecto.get("carpeta", ""),
            "proceso": raw.get("proceso") or raw.get("descripcion") or "",
            "pasos": raw.get("pasos") or [],
            "reglas": raw.get("reglas") or [],
            "triggers": triggers,
            "ubicacion": raw.get("ubicacion") or "personal",
            "instalar": raw.get("instalar", True),
            "incluir_reference": raw.get("incluir_reference", bool(raw.get("pasos_detalle"))),
            "creado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(ctx.paths["context"], context)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["context"])], notes=f"{nombre} ({tipo})")

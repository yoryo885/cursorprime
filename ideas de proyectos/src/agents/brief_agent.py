"""Agente 1: convierte idea JSON/texto en brief estructurado."""

from __future__ import annotations

from src.config import save_json, slugify
from src.models import AgentResult, PipelineContext


class BriefAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = ctx.idea
        slug = (
            ctx.slug
            or str(idea.get("slug") or "").strip()
            or slugify(str(idea.get("titulo") or idea.get("problema") or "proyecto"))
        )

        brief = {
            "nombre": idea.get("titulo") or idea.get("nombre") or slug,
            "slug": slug,
            "problema": idea.get("problema", ""),
            "usuario_final": idea.get("cliente_objetivo") or idea.get("usuario_final", ""),
            "modelo_negocio": idea.get("modelo_negocio", ""),
            "entrada": idea.get("entrada") or ["datos del dominio", "config del cliente"],
            "salida": idea.get("salida") or ["dashboard/reporte", "artefactos JSON"],
            "integraciones": idea.get("integraciones") or idea.get("urls_referencia") or [],
            "restricciones": {
                "mercado": idea.get("mercado", ""),
                "moneda": idea.get("moneda", ""),
                "semi_automatico": idea.get("semi_automatico", True),
            },
            "hipotesis": idea.get("hipotesis") or [],
            "notas": idea.get("notas", ""),
            "supuestos": [
                "MVP semi-automático hasta validar márgenes" if idea.get("semi_automatico", True) else "Full-auto si APIs lo permiten",
            ],
        }

        out = ctx.borrador_dir / "meta" / "brief.json"
        save_json(out, brief)
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"Brief para {slug}")

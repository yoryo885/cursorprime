"""Agente: genera ideas categorizadas — estado pendiente_aprobacion."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.config import CATEGORIAS_IDEA, load_json, save_json
from src.types import AgentResult, PipelineContext


def _idea(
    categoria: str,
    titulo: str,
    problema: str,
    propuesta: str,
    proyecto: str,
    confidence: float,
    origen: str,
) -> dict:
    return {
        "id": f"idea-{uuid4().hex[:8]}",
        "categoria": categoria,
        "titulo": titulo,
        "problema": problema,
        "propuesta": propuesta,
        "proyecto_afectado": proyecto,
        "confidence": confidence,
        "estado": "pendiente_aprobacion",
        "origen": origen,
        "creado_at": datetime.now(timezone.utc).isoformat(),
    }


class IdeaGeneratorAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        analisis = load_json(ctx.paths["analisis"], {})
        tema = context.get("tema") or ctx.slug
        oportunidades = analisis.get("oportunidades_pipeline") or context.get("oportunidades") or []

        ideas: list[dict] = []

        # visual
        ideas.append(
            _idea(
                "visual",
                "Pack promocional automático post-investigación",
                "Tras analizar un nicho no hay assets visuales listos para validar demanda.",
                "Conectar análisis → creador de contenido (3 PNG + 1 GIF del nicho detectado).",
                "creador de contenido",
                0.7,
                tema,
            )
        )

        # informacion
        ideas.append(
            _idea(
                "informacion",
                "Radar de nichos KDP desde YouTube semanal",
                "La investigación es manual y no se repite en cadencia.",
                "Pipeline investigación programable: queries fijas + informe JSON cada semana.",
                "lluvia-de-ideas",
                0.75,
                tema,
            )
        )
        for op in oportunidades[:2]:
            ideas.append(
                _idea(
                    "nuevo_proyecto",
                    op.get("titulo") or "Nuevo pipeline detectado",
                    f"Oportunidad detectada en investigación sobre {tema}.",
                    op.get("razon") or "Automatizar flujo que hoy es manual en YouTube/foros.",
                    "ideas de proyectos",
                    float(op.get("confidence") or 0.6),
                    "analisis",
                )
            )

        # marketing
        ideas.append(
            _idea(
                "marketing",
                "Landing «vende tu pipeline» para primer sistema empaquetado",
                "No hay página que venda el sistema una vez validado el pipeline.",
                "Copy + demo video corto del pipeline funcionando; precio fase beta.",
                "cursorprime",
                0.65,
                tema,
            )
        )

        # meta
        ideas.append(
            _idea(
                "meta",
                "Enlace investigación → evaluar-idea → construir",
                "Las ideas no fluyen solas hacia ideas de proyectos.",
                "Al aprobar idea en cola, generar borrador JSON en ideas de proyectos automáticamente.",
                "ideas de proyectos",
                0.8,
                "direccion",
            )
        )

        for cat in CATEGORIAS_IDEA:
            if not any(i["categoria"] == cat for i in ideas):
                ideas.append(
                    _idea(
                        cat,
                        f"Explorar mejora en {cat}",
                        f"Gap en categoría {cat} para {tema}.",
                        "Definir con el usuario en chat.",
                        "general",
                        0.4,
                        "fallback",
                    )
                )

        payload = {
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "tema": tema,
            "total": len(ideas),
            "ideas": ideas,
        }
        save_json(ctx.paths["ideas"], payload)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["ideas"])], notes=f"{len(ideas)} ideas generadas")

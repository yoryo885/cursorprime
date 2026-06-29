"""Agente: sintetiza hallazgos en análisis accionable."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


def _extract_patterns(youtube: list, web: list, tema: str) -> dict:
    text = " ".join(
        (i.get("titulo") or "") + " " + (i.get("snippet") or "")
        for i in youtube + web
    ).lower()

    productos = []
    if any(k in text for k in ("kdp", "amazon", "ebook", "kindle")):
        productos.append("Resúmenes / guías digitales en Amazon KDP")
    if any(k in text for k in ("ia", "chatgpt", "automat", "pipeline")):
        productos.append("Sistemas semi-automatizados con IA (investigar → producir)")
    if any(k in text for k in ("youtube", "faceless", "canal")):
        productos.append("Contenido YouTube + producto digital emparejado")
    if any(k in text for k in ("plantilla", "sistema", "curso")):
        productos.append("Venta del sistema/plantilla, no solo el producto final")

    oportunidades = [
        {
            "titulo": f"Pipeline investigación → producto para: {tema}",
            "razon": "Varios resultados muestran flujo manual replicable por agentes.",
            "confidence": 0.65,
        },
        {
            "titulo": "Empaquetar pipeline como producto vendible",
            "razon": "Foros y videos mencionan vender sistemas además del ebook.",
            "confidence": 0.6,
        },
    ]

    return {
        "tema": tema,
        "generado_at": datetime.now(timezone.utc).isoformat(),
        "resumen_ejecutivo": (
            f"Investigación sobre «{tema}»: demanda en KDP/guias digitales, "
            "creadores combinan YouTube + ebook, oportunidad en automatizar el pipeline completo."
        ),
        "productos_que_funcionan": productos or ["Productos digitales de nicho en marketplaces"],
        "patrones": [
            "Investigación de nicho antes de producir",
            "Contenido gratis (YouTube) → producto de pago",
            "Profesionalización por rol (no genérico)",
            "Vender el método/sistema además del entregable",
        ],
        "oportunidades_pipeline": oportunidades,
        "fuentes": [
            {"tipo": i.get("fuente"), "titulo": i.get("titulo"), "url": i.get("url")}
            for i in (youtube + web)[:12]
        ],
        "siguiente_paso_sugerido": "Correr pipeline lluvia para generar ideas con tu aprobación.",
    }


class SynthesisAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        fetch = load_json(ctx.paths["fetch"], {})
        tema = context.get("tema") or ctx.slug

        analisis = _extract_patterns(
            fetch.get("youtube") or [],
            fetch.get("web") or [],
            tema,
        )
        save_json(ctx.paths["analisis"], analisis)
        return AgentResult(ok=True, artifacts=[str(ctx.paths["analisis"])], notes=analisis["resumen_ejecutivo"][:80])

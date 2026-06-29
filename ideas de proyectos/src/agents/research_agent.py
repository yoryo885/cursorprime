"""Agente 2: plan de investigación y señales iniciales."""

from __future__ import annotations

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class ResearchAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = load_json(ctx.borrador_dir / "meta" / "brief.json", {})
        urls = brief.get("integraciones") or []

        research = {
            "slug": ctx.slug,
            "confidence": "baja",
            "pendiente_manual": True,
            "fuentes": urls,
            "checklist_investigacion": [
                "Confirmar si proveedor tiene API oficial o solo web",
                "Obtener comisiones reales vía API listing_prices ML (site MLC)",
                "Muestrear 10–20 SKUs: precio compra vs precio venta ML",
                "Identificar costo envío y devoluciones típicas",
                "Validar ToS del proveedor para scraping",
            ],
            "integraciones_detectadas": {
                "mercado_libre": "API oficial developers.mercadolibre.com",
                "proveedor_web": "Scrape Playwright — sin API confirmada",
            },
            "stack_sugerido": ["Python 3.9+", "argparse", "playwright", "python-dotenv", "anthropic (opcional)"],
            "riesgos": [
                "Proveedor sin API → scraping frágil",
                "Márgenes finos en productos baratos",
                "Stock desactualizado → cancelaciones ML",
            ],
        }

        out = ctx.borrador_dir / "meta" / "research.json"
        save_json(out, research)
        return AgentResult(ok=True, artifacts=[str(out)], notes="Research template — completar con datos reales")

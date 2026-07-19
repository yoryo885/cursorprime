from __future__ import annotations

import re

from src.config import save_json, slug_meta, slug_output
from src.types import AgentResult, PipelineContext


def _strip_html(html: str) -> str:
    t = re.sub(r"<br\s*/?>", "\n", html or "")
    t = re.sub(r"<[^>]+>", "", t)
    return t.strip()


class CopyAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        kdp = ctx.kdp
        marca = ctx.marca
        prod = marca.get("producto_piloto", {})
        ux = marca.get("ux_landing", {})
        cat = ux.get("copy_catalogo", {})
        beneficios = kdp.get("beneficios") or []
        copy = {
            "announce": "Descarga instantánea · Guías PDF en español · Serie «Aplicar en tu rol» · Primera compra 10% off",
            "hero_title": cat.get("hero_title", "Guías PDF para tu rol profesional"),
            "hero_subtitle": cat.get("hero_subtitle", marca.get("descripcion_corta", "")),
            "hero_cta": cat.get("hero_cta", "Ver guías"),
            "hero_brand": cat.get("hero_brand", marca.get("marca", "Vértice Pro").upper()),
            "hero_series": cat.get("hero_series", f"Serie · {marca.get('serie', 'Aplicar en tu rol')}"),
            "hero_label": cat.get("hero_label", marca.get("marca", "Vértice Pro").upper()),
            "guias_lead": cat.get("guias_lead", ""),
            "benefits_title": cat.get("benefits_title", "Qué incluye cada guía"),
            "benefits": cat.get("benefits") or [
                {"title": "Plan de 10 semanas", "text": "Una acción concreta por semana."},
                {"title": "Adaptado a tu rol", "text": "Pensado para tu oficio, no genérico."},
                {"title": "PDF tuyo para siempre", "text": "Compras, descargas y empiezas hoy."},
            ],
            "products_title": "Guías disponibles",
            "product": {
                "titulo": prod.get("titulo") or kdp.get("titulo", "").split(":")[0],
                "subtitulo": prod.get("subtitulo", ""),
                "precio": marca.get("precio_display", "$4.99"),
                "descripcion_corta": kdp.get("analisis", {}).get("propuesta_valor", "")[:200],
                "descripcion_html": kdp.get("descripcion_html", ""),
                "descripcion_plain": _strip_html(kdp.get("descripcion_html", ""))[:600] + "…",
                "beneficios": beneficios[:5],
            },
            "about_title": marca.get("marca", "Vértice Pro"),
            "about_text": cat.get("about_text", f"Editorial digital en español. Serie «{marca.get('serie', 'Aplicar en tu rol')}»."),
            "about_tagline": cat.get("about_tagline", ""),
            "footer_legal": "Estas guías son resúmenes independientes. No están afiliadas ni respaldadas por los autores ni editoriales de los libros originales.",
        }
        ctx.copy = copy
        save_json(slug_output(ctx.slug) / "copy" / "home.json", copy)
        return AgentResult(ok=True, data=copy)

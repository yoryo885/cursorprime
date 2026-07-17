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
        beneficios = kdp.get("beneficios") or []
        copy = {
            "announce": f"Descarga instantánea · Guías PDF en español · Serie «{marca.get('tagline', 'Aplicar en tu rol')}»",
            "hero_title": "Aplica libros famosos a tu trabajo esta semana",
            "hero_subtitle": marca.get("descripcion_corta", ""),
            "hero_cta": "Ver guías PDF",
            "benefits_title": "Qué incluye cada guía",
            "benefits": [
                {"title": "Plan de 10 semanas", "text": beneficios[3] if len(beneficios) > 3 else "Una acción concreta por semana."},
                {"title": "Adaptado a tu rol", "text": beneficios[0] if beneficios else "Pensado para tu oficio."},
                {"title": "Descarga al instante", "text": "Compras, descargas y empiezas hoy."},
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
            "about_text": f"Editorial digital en español. Serie «{marca.get('serie', 'Aplicar en tu rol')}». Guías accionables para {prod.get('audiencia', 'profesionales')}.",
            "footer_legal": "Estas guías son resúmenes independientes. No están afiliadas ni respaldadas por los autores ni editoriales de los libros originales.",
        }
        ctx.copy = copy
        save_json(slug_output(ctx.slug) / "copy" / "home.json", copy)
        return AgentResult(ok=True, data=copy)

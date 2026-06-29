"""Restricciones de título Amazon cuando la portada PDF está aprobada."""
from __future__ import annotations

from src.marketing.context_loader import MarketingContext


def titulo_constraints_block(ctx: MarketingContext | None) -> str:
    if not ctx or not ctx.portada_aprobada or not ctx.titulo_pdf:
        return ""
    return f"""
RESTRICCIÓN DE ALINEACIÓN CON EL PDF (portada aprobada por el editor):
- Título en portada del PDF (NO cambiar el sentido): «{ctx.titulo_pdf}»
- El título Amazon puede optimizar SEO pero DEBE:
  • Mencionar «{ctx.titulo_pdf}» o sus elementos clave (ej. «10 semanas» si aparece)
  • NO contradecir el formato prometido (semanas, rol, libro fuente)
  • NO reemplazar «Resumen personal» ni pedir cambiar la portada del PDF
"""


def postprocess_titulo(titulo: str, ctx: MarketingContext | None) -> str:
    """Asegura frase clave del PDF en el título KDP cuando la portada está congelada."""
    if not ctx or not ctx.portada_aprobada or not ctx.titulo_pdf:
        return titulo
    ref = ctx.titulo_pdf.lower()
    out = titulo.strip()
    if "10 semanas" in ref and "10 semana" not in out.lower():
        if len(out) + 14 <= 200:
            out = f"{out} · 10 semanas"
    return out[:200]

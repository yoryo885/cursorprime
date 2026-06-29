"""Agente 3: descripción HTML para Amazon KDP (300-400 palabras)."""
from __future__ import annotations

from src.llm import LLMClient
from src.marketing.agents.audience_intelligence_agent import AudienceIntelligence
from src.marketing.brief import MarketingBrief
from src.marketing.context_loader import MarketingContext
from src.marketing.models import PDFAnalysis
from src.marketing.utils import format_extra_instructions, parse_json_response, sanitize_kdp_text
from src.serie import load_serie_config


class DescriptionAgent:
    def run(
        self,
        llm: LLMClient,
        analisis: PDFAnalysis,
        titulo: str,
        marketing_ctx: MarketingContext | None = None,
        brief: MarketingBrief | None = None,
        intelligence: AudienceIntelligence | None = None,
        extra_instructions: list[str] | None = None,
        qc_feedback: str = "",
    ) -> tuple[str, list[str]]:
        cfg = load_serie_config()
        serie = str(cfg.get("nombre_serie") or "Aplicar en tu rol")
        marca = str(cfg.get("marca_editorial") or "Libros a Entender")
        disclaimer = str(cfg.get("disclaimer_kdp") or "").strip()
        elementos = ""
        if brief:
            elementos = "\n".join(f"- {e}" for e in brief.elementos_obligatorios)
        elif marketing_ctx and marketing_ctx.elementos_producto:
            elementos = "\n".join(f"- {e}" for e in marketing_ctx.elementos_producto)

        brief_block = ""
        if brief:
            brief_block = f"\nBRIEF DE MARKETING:\n{brief.to_prompt_block()}\n"

        intel_block = ""
        if intelligence:
            intel_block = f"\nINTELIGENCIA DE AUDIENCIA:\n{intelligence.to_prompt_block()}\n"

        prompt = f"""Eres copywriter para Amazon KDP en español.
{brief_block}{intel_block}
PRODUCTO:
- Título Amazon: {titulo}
- Serie (solo KDP): {serie} ({marca})
- Tema: {analisis.tema_principal}
- Libro fuente: {analisis.libro_fuente}
- Audiencia: {analisis.audiencia}
- Propuesta: {analisis.propuesta_valor}
- Contenido: {analisis.resumen_ejecutivo}
- Temas clave: {", ".join(analisis.temas_clave[:8])}

ELEMENTOS VERIFICABLES DEL PDF (menciona todos los que apliquen):
{elementos or "(inferir del análisis)"}

Escribe la descripción del producto para Amazon.

REGLAS:
- Entre 300 y 400 palabras en español
- Formato HTML básico permitido: <b>, <i>, <br>, listas con • en texto
- Explica qué aprenderá el comprador y por qué le conviene
- Menciona elementos concretos del PDF (mapa, tarjetas, plan de acción) si aplican
- Cierra con aviso legal en párrafo <b>Importante:</b>
- Disclaimer legal: {disclaimer}
- PROHIBIDO: "el mejor", "número uno", "#1", "gratis", promesas exageradas
{format_extra_instructions(extra_instructions)}
{f"CORREGIR EN ESTE INTENTO: {qc_feedback}" if qc_feedback else ""}
Responde SOLO con JSON:
{{
  "descripcion_html": "...",
  "beneficios": [
    "beneficio 1 (frase corta)",
    "beneficio 2",
    "beneficio 3",
    "beneficio 4",
    "beneficio 5"
  ]
}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        descripcion = sanitize_kdp_text(str(data.get("descripcion_html", "") or ""))
        beneficios = [
            sanitize_kdp_text(str(b))
            for b in data.get("beneficios", [])
            if b
        ][:5]
        while len(beneficios) < 5:
            beneficios.append("")
        return descripcion, beneficios[:5]

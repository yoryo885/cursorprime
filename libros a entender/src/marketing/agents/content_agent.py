"""Agente 1: lee y entiende el contenido del PDF."""
from __future__ import annotations

from src.llm import LLMClient
from src.marketing.agents.audience_intelligence_agent import AudienceIntelligence
from src.marketing.brief import MarketingBrief
from src.marketing.context_loader import MarketingContext
from src.marketing.models import PDFAnalysis
from src.marketing.pdf_reader import PDFContent
from src.marketing.utils import format_extra_instructions, load_contexto_cercano, parse_json_response


class ContentAgent:
    def run(
        self,
        llm: LLMClient,
        pdf: PDFContent,
        marketing_ctx: MarketingContext | None = None,
        brief: MarketingBrief | None = None,
        intelligence: AudienceIntelligence | None = None,
        contexto_extra: dict | None = None,
        extra_instructions: list[str] | None = None,
    ) -> PDFAnalysis:
        ctx = load_contexto_cercano(pdf.path)
        if contexto_extra:
            ctx.update(contexto_extra)

        ctx_block = ""
        if brief:
            ctx_block = (
                f"\nBRIEF DE MARKETING (prioridad sobre inferencias del PDF):\n"
                f"{brief.to_prompt_block()}\n"
            )
        elif marketing_ctx:
            ctx_block = (
                f"\nCONTEXTO ESTRUCTURADO DE PRODUCCIÓN (prioridad sobre inferencias del PDF):\n"
                f"{marketing_ctx.to_prompt_block()}\n"
            )
        elif ctx:
            import json

            ctx_block = f"\nCONTEXTO ADICIONAL DEL PROYECTO:\n{json.dumps(ctx, ensure_ascii=False, indent=2)}\n"

        intel_block = ""
        if intelligence:
            intel_block = (
                f"\nINTELIGENCIA DE AUDIENCIA (recolector + comparativas):\n"
                f"{intelligence.to_prompt_block()}\n"
            )

        prompt = f"""Eres un analista de productos digitales en español.

Lee el contenido extraído de un PDF (resumen/guía de libro) y deduce de qué trata.
{intel_block}
ARCHIVO: {pdf.nombre_archivo}
PÁGINAS: {pdf.num_paginas}
{ctx_block}
CONTENIDO DEL PDF:
{pdf.texto_para_llm}
{format_extra_instructions(extra_instructions)}
Responde SOLO con JSON válido:
{{
  "tema_principal": "tema central en una frase",
  "libro_fuente": "título y autor del libro original si aparece, o vacío",
  "audiencia": "a quién va dirigido (rol/profesión concreta)",
  "propuesta_valor": "qué problema resuelve para esa audiencia",
  "temas_clave": ["tema 1", "tema 2", "..."],
  "tono": "tono del material (ej. directo, práctico, editorial)",
  "resumen_ejecutivo": "3-4 oraciones sobre qué contiene el PDF"
}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        return PDFAnalysis(
            tema_principal=str(data.get("tema_principal", "") or ""),
            libro_fuente=str(data.get("libro_fuente", "") or pdf.titulo_inferido),
            audiencia=str(data.get("audiencia", "") or (brief.audiencia_oficial if brief else "") or (marketing_ctx.audiencia if marketing_ctx else "") or ctx.get("audiencia", "")),
            propuesta_valor=str(data.get("propuesta_valor", "") or ""),
            temas_clave=[str(t) for t in data.get("temas_clave", []) if t][:12],
            tono=str(data.get("tono", "") or ""),
            resumen_ejecutivo=str(data.get("resumen_ejecutivo", "") or ""),
        )

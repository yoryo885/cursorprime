"""Agente 2: título comercial para Amazon KDP (máx. 200 caracteres)."""
from __future__ import annotations

from src.llm import LLMClient
from src.marketing.agents.audience_intelligence_agent import AudienceIntelligence
from src.marketing.brief import MarketingBrief
from src.marketing.context_loader import MarketingContext
from src.marketing.models import PDFAnalysis
from src.marketing.title_constraints import postprocess_titulo, titulo_constraints_block
from src.marketing.utils import format_extra_instructions, parse_json_response, sanitize_kdp_text
from src.serie import load_serie_config


class TitleAgent:
    def run(
        self,
        llm: LLMClient,
        analisis: PDFAnalysis,
        marketing_ctx: MarketingContext | None = None,
        brief: MarketingBrief | None = None,
        intelligence: AudienceIntelligence | None = None,
        extra_instructions: list[str] | None = None,
    ) -> tuple[str, list[str]]:
        cfg = load_serie_config()
        serie = str(cfg.get("nombre_serie") or "Aplicar en tu rol")
        seed_titulo = ""
        ctx = brief.ctx if brief else marketing_ctx
        if brief and brief.seed_titulo_kdp and not brief.seed_obsoleto:
            seed_titulo = brief.seed_titulo_kdp
        elif ctx and ctx.kdp_seed:
            seed_titulo = str(ctx.kdp_seed.get("titulo_kdp") or "")

        constraints = brief.to_constraints_block() if brief else titulo_constraints_block(marketing_ctx)

        intel_block = ""
        if intelligence:
            intel_block = f"\nINTELIGENCIA DE AUDIENCIA:\n{intelligence.to_prompt_block()}\n"

        prompt = f"""Eres experto en títulos para Amazon KDP en español (México y España).
{intel_block}
SERIE DEL PRODUCTO (solo para Amazon, no para portada PDF): {serie}
BORRADOR DE REFERENCIA (meta/kdp_listing.json): {seed_titulo or "(ninguno)"}{" — OBSOLETO vs portada aprobada; ignorar" if brief and brief.seed_obsoleto else ""}
ANÁLISIS DEL PDF:
- Tema principal: {analisis.tema_principal}
- Libro fuente: {analisis.libro_fuente}
- Audiencia: {analisis.audiencia}
- Propuesta de valor: {analisis.propuesta_valor}
- Temas clave: {", ".join(analisis.temas_clave[:8])}
{titulo_constraints_block(marketing_ctx) if not brief else constraints}
Escribe UN título comercial para vender este ebook en Amazon.

REGLAS OBLIGATORIAS:
- Máximo 200 caracteres
- Español natural, con palabras que la gente busca
- Formato sugerido: "{{Concepto}} para {{rol en plural}}: {{beneficio concreto}}"
- Debe dejar claro que es guía/resumen aplicado al rol, NO el libro original
- PROHIBIDO: "el mejor", "número uno", "#1", "gratis", superlativos vacíos
- Sin comillas en el título
{format_extra_instructions(extra_instructions)}
Responde SOLO con JSON:
{{"titulo": "...", "alternativas": ["...", "..."]}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        titulo = sanitize_kdp_text(str(data.get("titulo", "") or ""))
        titulo = postprocess_titulo(titulo, ctx)
        if len(titulo) > 200:
            titulo = titulo[:197].rstrip() + "..."
        alternativas = [
            sanitize_kdp_text(str(a))[:200]
            for a in data.get("alternativas", [])
            if a
        ][:3]
        return titulo, alternativas

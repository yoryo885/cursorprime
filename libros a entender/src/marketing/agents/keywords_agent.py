"""Agente 4: 7 keywords para posicionar en Amazon."""
from __future__ import annotations

from src.llm import LLMClient
from src.marketing.agents.audience_intelligence_agent import AudienceIntelligence
from src.marketing.brief import MarketingBrief
from src.marketing.context_loader import MarketingContext
from src.marketing.models import PDFAnalysis
from src.marketing.utils import format_extra_instructions, parse_json_response, sanitize_kdp_text
from src.serie import load_serie_config


class KeywordsAgent:
    def run(
        self,
        llm: LLMClient,
        analisis: PDFAnalysis,
        titulo: str,
        marketing_ctx: MarketingContext | None = None,
        brief: MarketingBrief | None = None,
        intelligence: AudienceIntelligence | None = None,
        extra_instructions: list[str] | None = None,
    ) -> list[str]:
        cfg = load_serie_config()
        serie = str(cfg.get("nombre_serie") or "Aplicar en tu rol")
        lexico = ", ".join(brief.lexico_rol[:10]) if brief else (", ".join(marketing_ctx.lexico_rol[:10]) if marketing_ctx else "")
        kpis = ", ".join(brief.kpis_rol[:6]) if brief else (", ".join(marketing_ctx.kpis_rol[:6]) if marketing_ctx else "")
        seed_kws = ""
        ctx = brief.ctx if brief else marketing_ctx
        if ctx and ctx.kdp_seed.get("keywords") and not (brief and brief.seed_obsoleto):
            seed_kws = ", ".join(ctx.kdp_seed["keywords"][:7])

        brief_block = ""
        if brief:
            brief_block = f"\nBRIEF DE MARKETING:\n{brief.to_prompt_block()}\n"

        intel_block = ""
        priority_kws = ""
        if intelligence:
            intel_block = f"\nINTELIGENCIA DE AUDIENCIA:\n{intelligence.to_prompt_block()}\n"
            if intelligence.keywords_prioritarias:
                priority_kws = ", ".join(intelligence.keywords_prioritarias[:10])

        prompt = f"""Eres especialista en SEO para Amazon KDP en español.
{brief_block}{intel_block}
PRODUCTO:
- Título: {titulo}
- Serie: {serie}
- Tema: {analisis.tema_principal}
- Audiencia: {analisis.audiencia}
- Libro fuente: {analisis.libro_fuente}
- Temas clave: {", ".join(analisis.temas_clave[:8])}
- Léxico del rol (priorizar): {lexico or "(general)"}
- KPIs del rol: {kpis or "(general)"}
- Keywords borrador: {seed_kws or "(ninguna)"}
- Keywords prioritarias (gaps/intención): {priority_kws or "(ninguna)"}

Genera exactamente 7 palabras clave (keywords) que la gente usaría para buscar este ebook.

REGLAS:
- Español (México/España)
- Frases de 2-4 palabras, separadas por espacio (como las usa KDP)
- Mezcla: tema + rol + intención de búsqueda
- Sin marcas registradas ajenas innecesarias
- Sin "gratis", "mejor", "#1"
{format_extra_instructions(extra_instructions)}
Responde SOLO con JSON:
{{"keywords": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6", "kw7"]}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        keywords = []
        for kw in data.get("keywords", []):
            limpio = sanitize_kdp_text(str(kw))
            if limpio and limpio not in keywords:
                keywords.append(limpio)
        return keywords[:7]

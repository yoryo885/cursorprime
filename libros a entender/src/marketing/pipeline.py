"""Orquestador de la pipeline de marketing Amazon KDP."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.config import ANTHROPIC_API_KEY
from src.llm import LLMClient
from src.marketing.agents.audience_intelligence_agent import AudienceIntelligence, AudienceIntelligenceAgent
from src.marketing.agents.alignment_agent import AlignmentAgent
from src.marketing.agents.content_agent import ContentAgent
from src.marketing.agents.context_agent import ContextAgent
from src.marketing.agents.description_agent import DescriptionAgent
from src.marketing.agents.keywords_agent import KeywordsAgent
from src.marketing.agents.learning_agent import MarketingLearningAgent
from src.marketing.agents.packager_agent import PackagerAgent
from src.marketing.agents.title_agent import TitleAgent
from src.marketing.context_loader import load_marketing_context
from src.marketing.learning import MarketingLearningSystem
from src.marketing.models import KDPListing
from src.marketing.pdf_reader import extract_pdf_content
from src.marketing.quality import validate_listing
from src.marketing.agents.production_feedback_agent import ProductionFeedbackAgent
from src.marketing.constitution import REGLA_IRREFUTABLE, assert_read_only_pdf
from src.serie import load_serie_config


class KDPMarketingPipeline:
    """
    Pipeline de marketing (separada de la producción de PDF):
    contexto → bot Amazon → audiencia → copy → alineación → listing
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        learning: Optional[MarketingLearningSystem] = None,
        *,
        sin_aprendizaje: bool = False,
        sin_bot: bool = False,
        bot_headless: bool = False,
    ):
        self.llm = llm or self._build_llm()
        self.learning = learning or MarketingLearningSystem()
        self.sin_aprendizaje = sin_aprendizaje
        self.sin_bot = sin_bot
        self.bot_headless = bot_headless

    @staticmethod
    def _build_llm() -> LLMClient:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "Falta ANTHROPIC_API_KEY en .env — necesaria para los agentes de marketing."
            )
        return LLMClient(api_key=ANTHROPIC_API_KEY)

    @staticmethod
    def _subtitulo_from_brief(brief) -> str:
        seed = brief.ctx.kdp_seed if brief.ctx else {}
        sub = str(seed.get("subtitulo_kdp") or "").strip()
        if sub:
            return sub[:200]
        if brief.libro_fuente and brief.serie_kdp:
            return f"Guía práctica · Serie {brief.serie_kdp} · {brief.libro_fuente}"[:200]
        return ""

    def run(self, pdf_path: str | Path) -> KDPListing:
        path = assert_read_only_pdf(Path(pdf_path))
        cfg = load_serie_config()
        marketing_ctx = load_marketing_context(path)

        print(f"\n🔒 {REGLA_IRREFUTABLE[:80]}...")
        print(f"   🤖 LLM: Claude ({self.llm.model})")

        instrucciones_previas = self.learning.instrucciones_globales()
        if instrucciones_previas:
            print(f"\n📚 Aplicando {len(instrucciones_previas)} mejoras de listings anteriores")

        print(f"\n📣 Pipeline Marketing KDP")
        print(f"   PDF: {path.name}")

        print("\n1/11 📄 Leyendo PDF (SOLO LECTURA)...")
        pdf = extract_pdf_content(path)
        print(f"   ✓ {pdf.num_paginas} páginas · {len(pdf.texto_completo):,} caracteres")

        print("\n2/11 🧭 Agente Contexto (brief unificado)...")
        brief = ContextAgent().run(pdf=pdf, marketing_ctx=marketing_ctx)
        for line in ContextAgent.summarize(brief):
            print(f"   ✓ {line}")
        for conflicto in brief.conflictos:
            print(f"   ⚠️  {conflicto}")

        if not self.sin_bot:
            print("\n3/11 🤖 Bot Amazon (audiencia real — autocompletado + competidores)...")
            try:
                from src.marketing.bot.amazon_research import AmazonResearchBot

                AmazonResearchBot().run(
                    brief.slug,
                    brief=brief,
                    headless=self.bot_headless,
                )
            except Exception as err:
                print(f"   ⚠️  Bot Amazon falló: {err}")
                print("   ↳ Continúo con datos locales. Usa --sin-bot para omitir.")
        else:
            print("\n3/11 🤖 Bot Amazon — omitido (--sin-bot)")

        print("\n4/11 🧠 Inteligencia de audiencia (comparativas)...")
        intel, intel_path = AudienceIntelligenceAgent().run(brief, pdf, post_listing=False)
        disc = intel.comparativa.get("discoverability_score", {})
        print(f"   ✓ Informe: {intel_path.name}")
        print(f"   ✓ Consultas sugeridas: {len(intel.audiencia.get('intencion_busqueda', {}).get('consultas_amazon_sugeridas', []))}")
        print(f"   ✓ Keywords prioritarias: {len(intel.keywords_prioritarias)}")
        if disc.get("faltan_datos_externos") and self.sin_bot:
            print("   ⚠️  Sin datos Amazon — ejecuta sin --sin-bot")

        print("\n5/11 📨 Revisión del PDF → producción...")
        ProductionFeedbackAgent().run(path)

        print("\n6/11 🔍 Agente Contenido (Claude)...")
        analisis = ContentAgent().run(
            self.llm,
            pdf,
            brief=brief,
            intelligence=intel,
            extra_instructions=self.learning.instrucciones_para("contenido"),
        )
        print(f"   ✓ Tema: {analisis.tema_principal[:80]}")
        if brief.audiencia_oficial:
            analisis.audiencia = brief.audiencia_oficial
        print(f"   ✓ Audiencia: {analisis.audiencia or '(por inferir)'}")

        print("\n7/11 ✏️  Agente Título (Claude)...")
        titulo, alternativas = TitleAgent().run(
            self.llm,
            analisis,
            brief=brief,
            intelligence=intel,
            extra_instructions=self.learning.instrucciones_para("titulo"),
        )
        print(f"   ✓ {titulo}")
        if alternativas:
            print(f"   ✓ {len(alternativas)} alternativas guardadas")

        print("\n8/11 📝 Agente Descripción (Claude)...")
        descripcion, beneficios = DescriptionAgent().run(
            self.llm,
            analisis,
            titulo,
            brief=brief,
            intelligence=intel,
            extra_instructions=self.learning.instrucciones_para("descripcion"),
        )
        palabras = len(descripcion.split())
        print(f"   ✓ Descripción ~{palabras} palabras · {len(beneficios)} beneficios")

        print("\n9/11 🔑 Agente Keywords (Claude)...")
        keywords = KeywordsAgent().run(
            self.llm,
            analisis,
            titulo,
            brief=brief,
            intelligence=intel,
            extra_instructions=self.learning.instrucciones_para("keywords"),
        )
        for kw in keywords:
            print(f"   · {kw}")

        seed = brief.ctx.kdp_seed if brief.ctx else {}
        listing = KDPListing(
            titulo=titulo,
            subtitulo=self._subtitulo_from_brief(brief),
            titulo_alternativas=alternativas,
            descripcion_html=descripcion,
            keywords=keywords,
            beneficios=beneficios,
            categorias_bisac=[
                str(c) for c in seed.get("categorias_bisac_sugeridas", []) if c
            ],
            mercados=[str(m) for m in seed.get("mercados", ["MX", "ES"]) if m],
            precio_usd=float(seed.get("precio_usd") or 3.99),
            analisis=analisis,
            pdf_origen=str(path),
            serie=str(cfg.get("nombre_serie") or brief.serie_kdp or ""),
            disclaimer=str(cfg.get("disclaimer_kdp") or seed.get("disclaimer") or ""),
            generado_en=KDPListing.now_iso(),
            seed_titulo_kdp=brief.seed_titulo_kdp,
            titulo_pdf=brief.titulo_pdf,
        )

        print("\n10/11 🎯 Agente Alineación...")
        listing, fixes = AlignmentAgent().run(listing, brief, llm=self.llm, use_llm=True)
        listing.alignment_fixes = fixes
        for fix in fixes:
            print(f"   ✓ {fix}")

        print("\n11/11 ✅ Control de calidad...")
        qc = validate_listing(listing, marketing_ctx=brief.ctx)
        listing.qc_score = qc.score
        listing.qc_issues = qc.issues
        listing.qc_warnings = qc.warnings
        print(f"   ✓ Score: {qc.score}/10 · {'OK' if qc.passed else 'Revisar'}")
        for w in qc.warnings[:5]:
            print(f"   ⚠️  {w}")

        if qc.issues:
            print("   ↻ Reintento de alineación con Claude...")
            listing, fixes2 = AlignmentAgent().run(
                listing, brief, llm=self.llm, qc=qc, use_llm=True
            )
            listing.alignment_fixes.extend(fixes2)
            qc = validate_listing(listing, marketing_ctx=brief.ctx)
            listing.qc_score = qc.score
            listing.qc_issues = qc.issues
            listing.qc_warnings = qc.warnings
            print(f"   ✓ Score tras reintento: {qc.score}/10")

        elif "descripcion_muy_corta" in qc.warnings:
            print("   ↻ Reintentando descripción (muy corta)...")
            feedback = "La descripción debe tener entre 300 y 400 palabras."
            descripcion, beneficios = DescriptionAgent().run(
                self.llm,
                analisis,
                titulo,
                brief=brief,
                intelligence=intel,
                extra_instructions=self.learning.instrucciones_para("descripcion"),
                qc_feedback=feedback,
            )
            listing.descripcion_html = descripcion
            listing.beneficios = beneficios
            listing, fixes3 = AlignmentAgent().run(listing, brief, llm=self.llm, use_llm=False)
            listing.alignment_fixes.extend(fixes3)
            qc = validate_listing(listing, marketing_ctx=brief.ctx)
            listing.qc_score = qc.score
            listing.qc_issues = qc.issues
            listing.qc_warnings = qc.warnings
            print(f"   ✓ Score tras reintento: {qc.score}/10")

        self.learning.log_qc_run(
            pdf_origen=str(path),
            titulo=listing.titulo,
            score=qc.score,
            issues=qc.issues,
            warnings=qc.warnings,
        )

        print("\n📦 Agente Empaquetador...")
        json_path, txt_path = PackagerAgent().run(listing, marketing_ctx=brief.ctx)
        print(f"   ✓ JSON: {json_path}")
        print(f"   ✓ TXT:  {txt_path}")

        intel_final, intel_final_path = AudienceIntelligenceAgent().run(
            brief, pdf, post_listing=True
        )
        disc_final = intel_final.comparativa.get("discoverability_score", {})
        print(f"\n🧠 Informe audiencia actualizado: {intel_final_path.name}")
        print(f"   ✓ Discoverability: {disc_final.get('score')}/10 ({disc_final.get('nivel')})")
        if listing.diff_vs_seed:
            print("   ✓ Diff vs borrador:")
            for k, v in listing.diff_vs_seed.items():
                print(f"     · {k}: {v[:70]}...")

        if not self.sin_aprendizaje:
            MarketingLearningAgent(self.learning).run(self.llm, listing, qc)

        ProductionFeedbackAgent().run(path, listing=listing)

        return listing

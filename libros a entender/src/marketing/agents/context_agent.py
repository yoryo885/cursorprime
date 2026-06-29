"""Agente 0: fusiona PDF + meta en un brief único para el resto de agentes."""
from __future__ import annotations

from src.marketing.brief import MarketingBrief, build_marketing_brief
from src.marketing.context_loader import MarketingContext, load_marketing_context
from src.marketing.pdf_reader import PDFContent
from pathlib import Path


class ContextAgent:
    """
    Determinista (sin LLM). Carga meta/, detecta conflictos y produce MarketingBrief.
    """

    def run(
        self,
        pdf: PDFContent | None = None,
        marketing_ctx: MarketingContext | None = None,
        pdf_path: Path | None = None,
    ) -> MarketingBrief:
        if marketing_ctx is None:
            if pdf is None and pdf_path is None:
                raise ValueError("ContextAgent necesita pdf, pdf_path o marketing_ctx")
            path = pdf_path or (pdf.path if pdf else None)
            marketing_ctx = load_marketing_context(Path(path))

        brief = build_marketing_brief(marketing_ctx, pdf=pdf)
        return brief

    @staticmethod
    def summarize(brief: MarketingBrief) -> list[str]:
        """Líneas para logging en pipeline."""
        lines = [
            f"Audiencia: {brief.audiencia_oficial or '(inferir del PDF)'}",
            f"Serie KDP: {brief.serie_kdp}",
        ]
        if brief.portada_aprobada:
            lines.append(f"Portada aprobada: «{brief.titulo_pdf}»")
        if brief.conflictos:
            lines.append(f"Conflictos: {len(brief.conflictos)}")
        lines.append(f"Elementos obligatorios: {len(brief.elementos_obligatorios)}")
        return lines

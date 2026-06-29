"""Agente recolector: audiencia + comparativas → kdp/audience_intelligence.json"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.marketing.brief import MarketingBrief
from src.marketing.constitution import assert_output_path_allowed
from src.marketing.intelligence.collector import AudienceDataCollector
from src.marketing.intelligence.comparative import ComparativeAnalyzer
from src.marketing.pdf_reader import PDFContent
from src.marketing.utils import kdp_output_dir


@dataclass
class AudienceIntelligence:
    generado_en: str = ""
    audiencia: dict[str, Any] = field(default_factory=dict)
    comparativa: dict[str, Any] = field(default_factory=dict)
    keywords_prioritarias: list[str] = field(default_factory=list)

    def to_prompt_block(self) -> str:
        persona = self.audiencia.get("persona", {})
        intent = self.audiencia.get("intencion_busqueda", {})
        recs = self.comparativa.get("recomendaciones", [])
        discover = self.comparativa.get("discoverability_score", {})
        payload = {
            "audiencia_oficial": persona.get("audiencia_oficial"),
            "reto": persona.get("reto"),
            "intento_fallido": persona.get("intento_fallido"),
            "lexico_rol": persona.get("lexico", [])[:10],
            "kpis_rol": persona.get("kpis", [])[:6],
            "consultas_amazon_a_cubrir": intent.get("consultas_amazon_sugeridas", [])[:10],
            "keywords_prioritarias": self.keywords_prioritarias[:10],
            "discoverability": discover.get("score"),
            "gaps_lexico": self.comparativa.get("gaps_keywords", {}).get("lexico_rol_ausente", []),
            "recomendaciones_descubrimiento": recs[:6],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


class AudienceIntelligenceAgent:
    """
    Recolecta datos internos + archivos externos opcionales (kdp/market_research.json).
    Sin LLM — rápido y reproducible.
    """

    OUTPUT_NAME = "audience_intelligence.json"

    def run(
        self,
        brief: MarketingBrief,
        pdf: PDFContent,
        *,
        post_listing: bool = False,
    ) -> tuple[AudienceIntelligence, Path]:
        collector = AudienceDataCollector()
        audience_data = collector.collect(brief, pdf=pdf)

        kdp_dir = assert_output_path_allowed(kdp_output_dir(pdf.path))
        comparativa = ComparativeAnalyzer().analyze(
            brief,
            audience_data,
            kdp_dir=kdp_dir,
        )

        intel = AudienceIntelligence(
            generado_en=datetime.now(timezone.utc).isoformat(),
            audiencia=audience_data,
            comparativa=comparativa,
            keywords_prioritarias=self._build_priority_keywords(
                audience_data, comparativa
            ),
        )

        out_path = kdp_dir / self.OUTPUT_NAME
        kdp_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "generado_en": intel.generado_en,
                    "modo": "post_listing" if post_listing else "pre_listing",
                    "audiencia": intel.audiencia,
                    "comparativa": intel.comparativa,
                    "keywords_prioritarias": intel.keywords_prioritarias,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return intel, out_path

    @staticmethod
    def _build_priority_keywords(
        audience_data: dict[str, Any],
        comparativa: dict[str, Any],
    ) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []

        def add(kw: str) -> None:
            k = kw.strip().lower()[:50]
            if k and k not in seen:
                seen.add(k)
                out.append(kw.strip()[:50])

        gaps = comparativa.get("gaps_keywords", {})
        for term in gaps.get("lexico_rol_ausente", [])[:3]:
            add(f"{term} guía")
        for q in gaps.get("consultas_sin_cubrir", [])[:4]:
            add(q)
        for s in gaps.get("sugerencias_amazon_sin_cubrir", [])[:3]:
            add(str(s))
        for q in audience_data.get("intencion_busqueda", {}).get(
            "terminos_alta_intencion", []
        )[:4]:
            add(q)

        return out[:12]

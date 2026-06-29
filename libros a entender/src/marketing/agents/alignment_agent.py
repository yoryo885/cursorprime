"""Agente de alineación: corrige listing vs brief antes del QC final."""
from __future__ import annotations

import re

from src.llm import LLMClient
from src.marketing.brief import MarketingBrief
from src.marketing.models import KDPListing
from src.marketing.quality import (
    MarketingQCReport,
    _audiencia_presente,
    _strip_html,
    _titulo_comercial_presente,
)
from src.marketing.title_constraints import postprocess_titulo
from src.marketing.utils import parse_json_response, sanitize_kdp_text


class AlignmentAgent:
    """
    Primero reglas deterministas; si quedan issues críticos, un pase con Claude.
    """

    def run(
        self,
        listing: KDPListing,
        brief: MarketingBrief,
        *,
        llm: LLMClient | None = None,
        qc: MarketingQCReport | None = None,
        use_llm: bool = True,
    ) -> tuple[KDPListing, list[str]]:
        fixes: list[str] = []
        ctx = brief.ctx

        titulo_antes = listing.titulo
        listing.titulo = postprocess_titulo(listing.titulo, ctx)
        if listing.titulo != titulo_antes:
            fixes.append("titulo: postprocess portada aprobada")

        if brief.portada_aprobada and brief.titulo_pdf:
            if not _titulo_comercial_presente(brief.titulo_pdf, listing.titulo):
                candidato = brief.titulo_pdf
                if len(listing.titulo) > 40 and len(candidato) + 2 + min(60, len(listing.titulo)) <= 200:
                    candidato = f"{brief.titulo_pdf}: {listing.titulo[:80].rstrip()}"
                listing.titulo = candidato[:200]
                fixes.append("titulo: reemplazado por frase de portada aprobada")

        listing.titulo = self._trim_titulo(listing.titulo)
        if len(listing.titulo) > 200:
            listing.titulo = listing.titulo[:197].rstrip() + "..."
            fixes.append("titulo: recortado a 200 chars")

        desc_antes = listing.descripcion_html
        listing.descripcion_html = self._align_descripcion(listing, brief)
        if listing.descripcion_html != desc_antes:
            fixes.append("descripcion: serie/audiencia/elementos inyectados")

        kw_antes = list(listing.keywords)
        listing.keywords = self._align_keywords(listing, brief)
        if listing.keywords != kw_antes:
            fixes.append("keywords: léxico del rol reforzado")

        critical = self._critical_issues(listing, brief, qc)
        if critical and use_llm and llm is not None:
            listing, llm_fixes = self._align_with_llm(llm, listing, brief, critical)
            fixes.extend(llm_fixes)

        return listing, fixes

    @staticmethod
    def _trim_titulo(titulo: str) -> str:
        return re.sub(r"\s+", " ", (titulo or "").strip())

    @staticmethod
    def _audiencia_para_copy(listing: KDPListing, brief: MarketingBrief) -> str:
        """Frase canónica de audiencia: prioriza meta oficial, luego análisis del PDF."""
        if brief.audiencia_oficial:
            return brief.audiencia_oficial.strip()
        return (listing.analisis.audiencia or "").strip()

    def _align_descripcion(self, listing: KDPListing, brief: MarketingBrief) -> str:
        desc = listing.descripcion_html or ""
        plain = _strip_html(desc).lower()

        if brief.serie_kdp and brief.serie_kdp.lower() not in plain:
            bloque = (
                f"<br><br>Guía de la serie <b>{brief.serie_kdp}</b>"
                f" ({brief.marca}): aplica ideas de libros de negocio y productividad "
                f"a tu rol profesional."
            )
            if "<br><br>" in desc:
                idx = desc.find("<br><br>", desc.find("<br><br>") + 1 if desc.count("<br><br>") > 1 else 0)
                desc = desc[:idx] + bloque + desc[idx:]
            else:
                desc = desc.rstrip() + bloque

        plain = _strip_html(desc)
        audiencia_inyectar = self._audiencia_para_copy(listing, brief)
        if audiencia_inyectar and not _audiencia_presente(audiencia_inyectar, plain):
            desc = desc.rstrip() + (
                f"<br><br><b>Para quién es:</b> {audiencia_inyectar}."
            )
            plain = _strip_html(desc)
        if brief.audiencia_oficial and not _audiencia_presente(brief.audiencia_oficial, plain):
            desc = desc.rstrip() + (
                f"<br><br>Diseñada para <b>{brief.audiencia_oficial}</b>."
            )

        if brief.semanas_plan and str(brief.semanas_plan) not in _strip_html(desc):
            desc = desc.rstrip() + (
                f"<br><br>Incluye plan de acción de <b>{brief.semanas_plan} semanas</b> "
                f"con acciones concretas semana a semana."
            )

        return desc

    def _align_keywords(self, listing: KDPListing, brief: MarketingBrief) -> list[str]:
        kws = [k.strip() for k in listing.keywords if k.strip()]
        if len(kws) < 7:
            while len(kws) < 7 and brief.lexico_rol:
                term = brief.lexico_rol[len(kws) % len(brief.lexico_rol)]
                kws.append(f"{term} guía práctica"[:50])
        if not brief.lexico_rol:
            return kws[:7]

        combined = " ".join(kws).lower()
        for term in brief.lexico_rol[:3]:
            if term.lower() not in combined and len(kws) >= 7:
                kws[-1] = f"{term} {brief.audiencia_oficial.split()[0] if brief.audiencia_oficial else 'profesional'}"[:50]
                combined = " ".join(kws).lower()
        return kws[:7]

    def _critical_issues(
        self,
        listing: KDPListing,
        brief: MarketingBrief,
        qc: MarketingQCReport | None,
    ) -> list[str]:
        issues: list[str] = []
        if qc:
            issues.extend(qc.issues)
        if brief.portada_aprobada and brief.titulo_pdf:
            if not _titulo_comercial_presente(brief.titulo_pdf, listing.titulo):
                issues.append("titulo_no_alineado_con_portada_pdf")
        plain = _strip_html(listing.descripcion_html)
        if len(plain.split()) < 280:
            issues.append("descripcion_muy_corta")
        return list(dict.fromkeys(issues))

    def _align_with_llm(
        self,
        llm: LLMClient,
        listing: KDPListing,
        brief: MarketingBrief,
        issues: list[str],
    ) -> tuple[KDPListing, list[str]]:
        prompt = f"""Eres editor de listings Amazon KDP en español.

Corrige SOLO lo necesario para resolver estos issues: {", ".join(issues)}

BRIEF (fuente de verdad):
{brief.to_prompt_block()}

LISTING ACTUAL:
- Título ({len(listing.titulo)} chars): {listing.titulo}
- Descripción HTML (~{len(_strip_html(listing.descripcion_html).split())} palabras)
- Keywords: {", ".join(listing.keywords)}

REGLAS:
- NO inventes elementos que no estén en elementos_obligatorios_en_copy
- Mantener disclaimer al final si ya existe
- Título máx. 200 caracteres
- Descripción 300-400 palabras en HTML (<b>, <br>, listas con •)
- 7 keywords en español, máx. 50 chars c/u
- Si portada_aprobada, el título debe reflejar titulo_pdf_aprobado

Responde SOLO JSON:
{{
  "titulo": "...",
  "descripcion_html": "...",
  "keywords": ["...", "..."]
}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        fixes = ["alignment: corrección con Claude"]

        titulo = sanitize_kdp_text(str(data.get("titulo") or listing.titulo))
        if titulo:
            listing.titulo = postprocess_titulo(titulo, brief.ctx)[:200]
        desc = str(data.get("descripcion_html") or "").strip()
        if desc:
            listing.descripcion_html = desc
        kws_raw = data.get("keywords")
        if isinstance(kws_raw, list) and len(kws_raw) >= 7:
            listing.keywords = [sanitize_kdp_text(str(k))[:50] for k in kws_raw[:7]]

        return listing, fixes

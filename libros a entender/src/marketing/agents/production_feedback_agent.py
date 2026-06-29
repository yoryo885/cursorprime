"""Agente puente: marketing detecta problemas del PDF y escala a producción."""
from __future__ import annotations

from pathlib import Path

from src.marketing.models import KDPListing
from src.marketing.production_handoff import crear_solicitud, infer_slug_from_pdf
from src.marketing.quality import PDFContentIssue, detect_pdf_content_issues


class ProductionFeedbackAgent:
    """
    NO modifica el PDF. Habla con producción vía logs/produccion_solicitudes.json.

    Agentes de producción que pueden atender solicitudes:
    - main_agent / PDFDesignAgent → portada, ensamblaje PDF
    - TablesAgent, MapAgent → contenido visual
    - AudienceIntroAgent, RolUsuarioAgent → audiencia y rol
    - ActionPlanAgent → plan de acción
    """

    AGENTE_POR_TIPO = {
        "portada": "PDFDesignAgent",
        "diseno": "PDFDesignAgent",
        "contenido": "main_agent",
        "audiencia": "AudienceIntroAgent",
        "rol": "RolUsuarioAgent",
        "plan_accion": "ActionPlanAgent",
        "mapa": "MapAgent",
        "tablas": "TablesAgent",
        "legal": "ActionPlanAgent",
    }

    def run(self, pdf_path: Path, listing: KDPListing | None = None) -> list[dict]:
        issues = detect_pdf_content_issues(pdf_path, listing=listing)
        if not issues:
            return []

        print(f"\n📨 ProductionFeedbackAgent: {len(issues)} problema(s) en el PDF")
        print("   (Marketing NO modifica el PDF — escalando a producción)")

        solicitudes = []
        for issue in issues:
            agente = self.AGENTE_POR_TIPO.get(issue.tipo, "main_agent")
            sol = crear_solicitud(
                pdf_origen=pdf_path,
                problema=issue.problema,
                solicitud=issue.solicitud,
                tipo=issue.tipo,
                prioridad=issue.prioridad,
                agente_destino=agente,
                contexto=issue.contexto,
            )
            solicitudes.append(sol)
            print(f"   → [{issue.prioridad}] {issue.tipo}: {issue.problema[:70]}...")
            print(f"     Agente destino: {agente}")

        slug = infer_slug_from_pdf(pdf_path)
        print(f"\n   ✓ Solicitudes en logs/produccion_solicitudes.json (slug: {slug})")
        print(f"   ✓ Producción debe actuar: python main.py --slug {slug} ...")
        return solicitudes

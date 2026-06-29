"""Extrae datos de audiencia desde fuentes internas del proyecto."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.config import MARKETING_ERRORES_LOG, ROLES_CATALOG_PATH
from src.marketing.brief import MarketingBrief
from src.marketing.pdf_reader import PDFContent
from src.serie import load_serie_config


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


class AudienceDataCollector:
    """Agrega persona, dolor, intención de búsqueda y señales del producto."""

    def collect(
        self,
        brief: MarketingBrief,
        pdf: PDFContent | None = None,
    ) -> dict[str, Any]:
        cfg = load_serie_config()
        familia = str(brief.ctx.rol_perfil.get("familia_rol") or "") if brief.ctx else ""
        hooks = cfg.get("hooks_por_familia_rol") or {}
        hook = str(hooks.get(familia) or hooks.get("generico") or "")

        persona = self._build_persona(brief)
        producto = self._build_product_signals(brief)
        search_intent = self._build_search_intent(brief, hook, pdf)
        historial = self._load_qc_historial(brief.slug)
        catalogo = self._load_roles_catalog()

        return {
            "slug": brief.slug,
            "persona": persona,
            "producto": producto,
            "intencion_busqueda": search_intent,
            "hook_familia_rol": hook,
            "mercados": cfg.get("mercados_amazon") or ["MX", "ES"],
            "historial_qc": historial,
            "roles_catalogo_disponibles": list(catalogo.keys()),
        }

    def _build_persona(self, brief: MarketingBrief) -> dict[str, Any]:
        ctx = brief.ctx
        return {
            "audiencia_oficial": brief.audiencia_oficial,
            "reto": brief.reto_usuario or (ctx.rol_perfil.get("reto") if ctx else ""),
            "intento_fallido": (
                str(ctx.contexto_usuario.get("intento_fallido") or "")
                if ctx
                else ""
            ) or str((ctx.rol_perfil.get("intento_fallido") if ctx else "") or ""),
            "lexico": brief.lexico_rol,
            "kpis": brief.kpis_rol,
            "metodologia": str(ctx.rol_perfil.get("metodologia") or "") if ctx else "",
            "prohibiciones": brief.prohibiciones[:8],
            "temas_plan": brief.temas_plan[:12],
        }

    def _build_product_signals(self, brief: MarketingBrief) -> dict[str, Any]:
        return {
            "titulo_pdf": brief.titulo_pdf,
            "portada_aprobada": brief.portada_aprobada,
            "libro_fuente": brief.libro_fuente,
            "elementos": brief.elementos_obligatorios,
            "semanas_plan": brief.semanas_plan,
            "plantilla_vacia": brief.plantilla_vacia,
            "serie_kdp": brief.serie_kdp,
        }

    def _build_search_intent(
        self,
        brief: MarketingBrief,
        hook: str,
        pdf: PDFContent | None,
    ) -> dict[str, Any]:
        rol = brief.audiencia_oficial or "profesional"
        rol_corto = rol.split()[0] if rol else "profesional"
        concepto = self._infer_concepto(brief, pdf)
        queries = [
            f"{concepto} {rol_corto}",
            f"guía {concepto} {rol_corto}",
            f"aplicar {concepto} {rol}",
            f"{concepto} educación" if "escuela" in rol or "aula" in rol else f"{concepto} trabajo",
            f"plan acción {concepto}",
            f"productividad {rol_corto}",
        ]
        if hook:
            queries.append(f"{concepto} {hook}")
        if brief.semanas_plan:
            queries.append(f"{concepto} {brief.semanas_plan} semanas")

        for kpi in brief.kpis_rol[:3]:
            queries.append(f"{kpi} {rol_corto}")

        for term in brief.lexico_rol[:4]:
            queries.append(f"{term} {concepto}")

        seen: set[str] = set()
        unique: list[str] = []
        for q in queries:
            qn = re.sub(r"\s+", " ", q.strip().lower())
            if qn and qn not in seen:
                seen.add(qn)
                unique.append(q.strip())

        return {
            "concepto_principal": concepto,
            "consultas_amazon_sugeridas": unique[:15],
            "terminos_alta_intencion": [
                t for t in unique[:8]
                if any(w in t for w in ("guía", "plan", "aplicar", "priorizar"))
            ],
        }

    @staticmethod
    def _infer_concepto(brief: MarketingBrief, pdf: PDFContent | None) -> str:
        libro = brief.libro_fuente.lower()
        if "pareto" in libro:
            return "pareto"
        if pdf and pdf.titulo_inferido:
            words = re.findall(r"\w+", pdf.titulo_inferido.lower())
            skip = {"el", "la", "de", "del", "los", "las", "un", "una", "y", "en", "por"}
            for w in words:
                if len(w) > 4 and w not in skip:
                    return w
        if brief.temas_plan:
            return brief.temas_plan[0].split()[0].lower()
        return "productividad"

    def _load_qc_historial(self, slug: str) -> list[dict[str, Any]]:
        log = _read_json(MARKETING_ERRORES_LOG)
        if not isinstance(log, list):
            return []
        out = []
        for entry in log:
            if not isinstance(entry, dict):
                continue
            origen = str(entry.get("pdf_origen") or "")
            if slug in origen or f"/{slug}/" in origen:
                out.append({
                    "timestamp": entry.get("timestamp"),
                    "score": entry.get("score"),
                    "warnings": entry.get("warnings", []),
                    "issues": entry.get("issues", []),
                })
        return out[-5:]

    @staticmethod
    def _load_roles_catalog() -> dict[str, Any]:
        data = _read_json(ROLES_CATALOG_PATH)
        return data if isinstance(data, dict) else {}

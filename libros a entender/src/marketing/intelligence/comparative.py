"""Análisis comparativo: gaps de keywords, otros libros, competencia externa."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.config import RESUMENES_DIR
from src.marketing.brief import MarketingBrief


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", (text or "").lower()) if len(w) > 3}


class ComparativeAnalyzer:
    """
    Cruza datos internos + archivos opcionales en kdp/:
    - market_research.json  (búsquedas Amazon MX/ES)
    - competitors.json      (top ASINs del nicho)
    """

    MARKET_RESEARCH = "market_research.json"
    COMPETITORS = "competitors.json"

    def analyze(
        self,
        brief: MarketingBrief,
        audience_data: dict[str, Any],
        *,
        listing_path: Path | None = None,
        kdp_dir: Path | None = None,
    ) -> dict[str, Any]:
        slug_dir = RESUMENES_DIR / brief.slug
        kdp = kdp_dir or (slug_dir / "kdp")
        listing = self._load_listing(listing_path or kdp / "amazon_listing.json")
        seed = brief.ctx.kdp_seed if brief.ctx else {}
        external = self._load_external(kdp)
        otros_libros = self._compare_other_books(brief.slug)
        gaps = self._keyword_gaps(audience_data, listing, seed, external)
        discoverability = self._discoverability_score(
            brief, audience_data, listing, gaps, external
        )
        recomendaciones = self._recommendations(
            brief, audience_data, gaps, external, discoverability
        )

        return {
            "listing_actual": self._listing_summary(listing),
            "seed_kdp": {
                "titulo": seed.get("titulo_kdp"),
                "keywords": seed.get("keywords", []),
                "obsoleto": brief.seed_obsoleto,
            },
            "datos_externos": external,
            "otros_libros_serie": otros_libros,
            "gaps_keywords": gaps,
            "discoverability_score": discoverability,
            "recomendaciones": recomendaciones,
        }

    def _load_listing(self, path: Path) -> dict[str, Any]:
        data = _read_json(path)
        return data if isinstance(data, dict) else {}

    def _load_external(self, kdp_dir: Path) -> dict[str, Any]:
        research = _read_json(kdp_dir / self.MARKET_RESEARCH)
        competitors = _read_json(kdp_dir / self.COMPETITORS)
        return {
            "market_research_presente": isinstance(research, dict),
            "competitors_presente": isinstance(competitors, dict),
            "busquedas_amazon": (
                research.get("busquedas", []) if isinstance(research, dict) else []
            ),
            "sugerencias_autocompletado": (
                research.get("sugerencias_autocompletado", [])
                if isinstance(research, dict)
                else []
            ),
            "competidores": (
                competitors.get("items", []) if isinstance(competitors, dict) else []
            ),
            "notas": (
                research.get("notas", "") if isinstance(research, dict) else ""
            ),
        }

    def _compare_other_books(self, slug_actual: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        if not RESUMENES_DIR.is_dir():
            return out
        for folder in sorted(RESUMENES_DIR.iterdir()):
            if not folder.is_dir() or folder.name == slug_actual:
                continue
            listing_path = folder / "kdp" / "amazon_listing.json"
            data = _read_json(listing_path)
            if not isinstance(data, dict) or not data.get("titulo"):
                continue
            analisis = data.get("analisis") if isinstance(data.get("analisis"), dict) else {}
            out.append({
                "slug": folder.name,
                "titulo": data.get("titulo"),
                "audiencia": analisis.get("audiencia", ""),
                "keywords": data.get("keywords", [])[:5],
                "qc_score": data.get("qc_score"),
            })
        return out

    def _keyword_gaps(
        self,
        audience_data: dict[str, Any],
        listing: dict[str, Any],
        seed: dict[str, Any],
        external: dict[str, Any],
    ) -> dict[str, Any]:
        listing_kws = [str(k).lower() for k in listing.get("keywords", [])]
        seed_kws = [str(k).lower() for k in seed.get("keywords", [])]
        combined = " ".join(listing_kws + [listing.get("titulo", "")]).lower()

        lexico = audience_data.get("persona", {}).get("lexico", [])
        faltan_lexico = [t for t in lexico if t.lower() not in combined]

        queries = audience_data.get("intencion_busqueda", {}).get(
            "consultas_amazon_sugeridas", []
        )
        faltan_intencion = [
            q for q in queries
            if not any(w in combined for w in _tokenize(q))
        ][:8]

        sugerencias_ext = external.get("sugerencias_autocompletado") or []
        faltan_externas = [
            s for s in sugerencias_ext
            if str(s).lower() not in combined
        ][:8]

        competidores = external.get("competidores") or []
        terminos_comp = set()
        for c in competidores:
            if isinstance(c, dict):
                terminos_comp.update(_tokenize(str(c.get("titulo", ""))))
                for kw in c.get("keywords_visibles", []) or []:
                    terminos_comp.update(_tokenize(str(kw)))
        faltan_vs_competencia = sorted(
            t for t in terminos_comp if t not in combined and len(t) > 4
        )[:10]

        return {
            "lexico_rol_ausente": faltan_lexico,
            "consultas_sin_cubrir": faltan_intencion,
            "sugerencias_amazon_sin_cubrir": faltan_externas,
            "terminos_competencia_sin_cubrir": faltan_vs_competencia,
            "keywords_listing": listing_kws,
            "keywords_seed": seed_kws,
        }

    def _discoverability_score(
        self,
        brief: MarketingBrief,
        audience_data: dict[str, Any],
        listing: dict[str, Any],
        gaps: dict[str, Any],
        external: dict[str, Any],
    ) -> dict[str, Any]:
        puntos = 0.0
        max_p = 10.0
        titulo = str(listing.get("titulo") or "").lower()
        kws = " ".join(listing.get("keywords", [])).lower()
        concepto = audience_data.get("intencion_busqueda", {}).get("concepto_principal", "")

        if concepto and concepto in titulo:
            puntos += 1.5
        if brief.audiencia_oficial and _tokenize(brief.audiencia_oficial) & _tokenize(titulo + " " + kws):
            puntos += 1.5
        if brief.semanas_plan and str(brief.semanas_plan) in titulo + kws:
            puntos += 1.0
        if len(listing.get("keywords", [])) >= 7:
            puntos += 1.5
        if not gaps.get("lexico_rol_ausente"):
            puntos += 1.5
        if len(gaps.get("consultas_sin_cubrir", [])) <= 3:
            puntos += 1.0
        if external.get("market_research_presente"):
            puntos += 1.0
        if external.get("competitors_presente"):
            puntos += 1.0

        score = round(min(10.0, (puntos / max_p) * 10), 1)
        return {
            "score": score,
            "nivel": "alta" if score >= 7 else "media" if score >= 5 else "baja",
            "faltan_datos_externos": not external.get("market_research_presente"),
        }

    def _recommendations(
        self,
        brief: MarketingBrief,
        audience_data: dict[str, Any],
        gaps: dict[str, Any],
        external: dict[str, Any],
        discoverability: dict[str, Any],
    ) -> list[str]:
        recs: list[str] = []
        concepto = audience_data.get("intencion_busqueda", {}).get("concepto_principal", "")
        rol = brief.audiencia_oficial

        if discoverability.get("faltan_datos_externos"):
            recs.append(
                f"Añade resumenes/{brief.slug}/kdp/market_research.json con búsquedas "
                "reales de Amazon MX/ES (autocompletado) para afinar keywords."
            )
        if not external.get("competitors_presente"):
            recs.append(
                f"Añade resumenes/{brief.slug}/kdp/competitors.json con 5 títulos rivales "
                "(ASIN, precio, keywords visibles) para comparar posicionamiento."
            )
        for term in gaps.get("lexico_rol_ausente", [])[:3]:
            recs.append(f"Incluir en keywords o título el término del rol: «{term}».")
        for q in gaps.get("consultas_sin_cubrir", [])[:3]:
            recs.append(f"Cubrir intención de búsqueda: «{q}».")
        if concepto and rol:
            recs.append(
                f"Título ideal para descubrimiento: «{concepto} para {rol}» + beneficio concreto."
            )
        if brief.semanas_plan:
            recs.append(
                f"Mantener «{brief.semanas_plan} semanas» visible en título o keywords — "
                "diferenciador frente a resúmenes genéricos."
            )
        return recs[:10]

    @staticmethod
    def _listing_summary(listing: dict[str, Any]) -> dict[str, Any]:
        if not listing:
            return {"presente": False}
        return {
            "presente": True,
            "titulo": listing.get("titulo"),
            "keywords": listing.get("keywords", []),
            "qc_score": listing.get("qc_score"),
        }

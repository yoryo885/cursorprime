from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class PDFAnalysis:
    """Resultado del agente que entiende el PDF."""

    tema_principal: str = ""
    libro_fuente: str = ""
    audiencia: str = ""
    propuesta_valor: str = ""
    temas_clave: list[str] = field(default_factory=list)
    tono: str = ""
    resumen_ejecutivo: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KDPListing:
    """Listing completo listo para Amazon KDP."""

    titulo: str = ""
    subtitulo: str = ""
    titulo_alternativas: list[str] = field(default_factory=list)
    descripcion_html: str = ""
    keywords: list[str] = field(default_factory=list)
    beneficios: list[str] = field(default_factory=list)
    categorias_bisac: list[str] = field(default_factory=list)
    mercados: list[str] = field(default_factory=list)
    precio_usd: float = 0.0
    analisis: PDFAnalysis = field(default_factory=PDFAnalysis)
    pdf_origen: str = ""
    serie: str = ""
    disclaimer: str = ""
    generado_en: str = ""
    qc_score: float = 0.0
    qc_issues: list[str] = field(default_factory=list)
    qc_warnings: list[str] = field(default_factory=list)
    seed_titulo_kdp: str = ""
    titulo_pdf: str = ""
    diff_vs_seed: dict[str, str] = field(default_factory=dict)
    alignment_fixes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = {
            "titulo": self.titulo,
            "subtitulo": self.subtitulo,
            "titulo_alternativas": self.titulo_alternativas,
            "descripcion_html": self.descripcion_html,
            "keywords": self.keywords,
            "beneficios": self.beneficios,
            "categorias_bisac": self.categorias_bisac,
            "mercados": self.mercados,
            "precio_usd": self.precio_usd,
            "analisis": self.analisis.to_dict(),
            "pdf_origen": self.pdf_origen,
            "serie": self.serie,
            "disclaimer": self.disclaimer,
            "generado_en": self.generado_en,
            "qc_score": self.qc_score,
            "qc_issues": self.qc_issues,
            "qc_warnings": self.qc_warnings,
            "seed_titulo_kdp": self.seed_titulo_kdp,
            "titulo_pdf": self.titulo_pdf,
            "diff_vs_seed": self.diff_vs_seed,
            "alignment_fixes": self.alignment_fixes,
        }
        return data

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

"""
models.py — estructuras de datos que circulan por todo el sistema.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.agents.book_package import BookPackage


@dataclass
class TopicResult:
    """Resultado de procesar un tema con Claude."""
    tema: str
    resumen: str = ""
    resumen_voz: str = ""
    fragmentos: list = field(default_factory=list)
    fallo: bool = False
    intentos: int = 1
    quality_score: float = 0.0
    quality_flags: list = field(default_factory=list)
    subagente_id: int = 0
    calidad_issues: list = field(default_factory=list)
    intro_tema: str = ""


@dataclass
class BookJob:
    """Descripción del trabajo a realizar."""
    pdf_path: str
    temas: list[str]
    max_subagentes: int = 4
    libro_slug: str = ""
    solo_enriquecer: bool = False
    sin_llm: bool = False
    sin_imagenes: bool = False
    sin_md: bool = False
    solo_mapa: bool = False
    solo_tablas: bool = False
    solo_pdf: bool = False
    solo_intros: bool = False
    solo_resumenes: bool = False
    solo_plan_accion: bool = False
    sin_qc: bool = False


@dataclass
class ProcessingOutput:
    """Resultado final del proceso completo."""
    libro_slug: str
    resultados: list[TopicResult]
    output_dir: str
    quality_report: dict = field(default_factory=dict)
    costo_real_usd: float = 0.0
    markdown_path: Optional[Path] = None
    pdf_path: Optional[Path] = None
    package: Optional["BookPackage"] = None

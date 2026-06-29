from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class TopicTable:
    """Tabla generada por el agente de tablas para un tema."""

    tema: str
    idea_clave: str
    ejemplo_practico: str
    aplicacion_vida_real: str
    image_path: Optional[Path] = None


@dataclass
class BookPackage:
    """Artefactos reunidos para el PDF final."""

    libro_nombre: str
    libro_slug: str
    output_dir: Path
    resultados: list
    tablas: list = field(default_factory=list)
    mapa_path: Optional[Path] = None
    imagenes: dict = field(default_factory=dict)
    introduccion: str = ""
    audiencia: str = ""
    fecha: Optional[datetime] = None
    pdf_path: Optional[Path] = None
    incluir_imagenes_pdf: bool = True

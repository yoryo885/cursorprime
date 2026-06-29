"""
CONSTITUCIÓN DEL SISTEMA DE MARKETING — REGLA IRREFUTABLE

Marketing (kdp_main.py, src/marketing/) NUNCA modifica PDFs de producción.
Si algo del PDF está mal, se escala al agente de producción vía solicitudes.
"""
from __future__ import annotations

from pathlib import Path

REGLA_IRREFUTABLE = (
    "La pipeline de marketing SOLO LEE el PDF. "
    "Está ESTRICTAMENTE PROHIBIDO crear, modificar, regenerar, "
    "sobrescribir o exportar una nueva versión del PDF de producción."
)

ROL_MARKETING = "maquetación comercial Amazon KDP (título, descripción, keywords)"
ROL_PRODUCCION = "fabricación del PDF editorial (main.py, src/agents/, src/main_agent.py)"

ACCION_SI_PDF_MAL = (
    "Registrar una solicitud en logs/produccion_solicitudes.json "
    "para que el agente de producción corrija el PDF. "
    "Marketing NO toca el archivo PDF."
)

OUTPUT_PERMITIDO = (
    "Marketing solo puede escribir en: "
    "resumenes/{slug}/kdp/*, logs/marketing_*.json, logs/produccion_solicitudes.json"
)


class MarketingPDFWriteForbidden(PermissionError):
    """Intento de modificar un PDF desde la capa de marketing."""


def assert_read_only_pdf(pdf_path: Path) -> Path:
    """
    Valida que la ruta es un PDF existente para lectura.
    Marketing nunca debe recibir rutas de salida de PDF aquí.
    """
    path = Path(pdf_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"PDF no encontrado (solo lectura): {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Se esperaba un PDF de producción, no: {path.suffix}")
    return path


def forbid_writing_pdf(target: Path, *, caller: str = "marketing") -> None:
    """Bloquea cualquier intento de escritura sobre un PDF desde marketing."""
    path = Path(target).resolve()
    if path.suffix.lower() == ".pdf":
        raise MarketingPDFWriteForbidden(
            f"[{caller}] PROHIBIDO modificar PDF: {path}\n"
            f"{REGLA_IRREFUTABLE}\n"
            f"Usa ProductionFeedbackAgent → logs/produccion_solicitudes.json"
        )


def assert_output_path_allowed(output_path: Path) -> Path:
    """Solo permite escribir en carpetas kdp/ o logs/ de marketing."""
    path = Path(output_path).resolve()
    forbid_writing_pdf(path, caller="marketing.output")

    parts = {p.lower() for p in path.parts}
    if "kdp" in parts or "logs" in parts:
        return path
    if path.name.startswith("marketing_") or path.name == "produccion_solicitudes.json":
        return path

    raise MarketingPDFWriteForbidden(
        f"Marketing no puede escribir en: {path}\n{OUTPUT_PERMITIDO}"
    )

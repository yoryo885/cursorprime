import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass
LIBROS_DIR = BASE_DIR / "libros"
RESUMENES_DIR = BASE_DIR / "resumenes"
LOGS_DIR = BASE_DIR / "logs"
ROLES_CATALOG_PATH = BASE_DIR / "meta" / "roles_catalog.json"
SERIE_CONFIG_PATH = BASE_DIR / "meta" / "serie_config.json"
PDF_CACHE_DIR = BASE_DIR / ".cache" / "pdf_text"
ERRORES_LOG = LOGS_DIR / "errores.json"
MEJORAS_LOG = LOGS_DIR / "mejoras.json"
MARKETING_MEJORAS_LOG = LOGS_DIR / "marketing_mejoras.json"
MARKETING_ERRORES_LOG = LOGS_DIR / "marketing_errores.json"
PRODUCCION_SOLICITUDES_LOG = LOGS_DIR / "produccion_solicitudes.json"

DEFAULT_MAX_SUBAGENTS = 4
CLAUDE_MODEL = "claude-sonnet-4-5"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
NAPKIN_API_KEY = os.environ.get("NAPKIN_API_KEY", "")
NAPKIN_API_BASE = os.environ.get("NAPKIN_API_BASE", "https://api.napkin.ai")

MAX_CANDIDATE_CHUNKS = 5
CHUNK_SIZE = 1500
MAX_TOKENS_SUMMARY = 2048
LLM_MAX_RETRIES = 5
LLM_RETRY_BUFFER_SECS = 2

INTRO_FILENAME = "introduccion.txt"
INTRO_AUDIENCIA_FILENAME = "intro_audiencia.txt"
VOZ_NOMBRE = "Yordy"
TEMA_RESUMEN_ETIQUETA = "Para ti"
AUTOR_OCUPACION = "Creador de contenido y resúmenes de libros"
AUTOR_BIO_CORTA = (
    "Leo, destilo y comparto ideas de libros para quien no tiene tiempo "
    "de leerlos enteros pero sí ganas de aplicar algo concreto."
)

POOR_SUMMARY_MIN_LENGTH = 150

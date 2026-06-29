import json
import re
import unicodedata
from typing import Optional

from src.llm import LLMClient

# Traducciones fijas para búsquedas en Unsplash (mejor relevancia en inglés).
TOPIC_TRANSLATIONS: dict[str, str] = {
    "sesgos cognitivos": "cognitive bias",
    "toma de decisiones": "decision making",
    "sistema 1 y sistema 2": "system 1 system 2 thinking",
    "heuristicas": "heuristics psychology",
    "emociones y razon": "emotion and reason",
    "memoria y experiencia": "memory and experience psychology",
    "comportamiento humano": "human behavior psychology",
    "errores de juicio": "judgment error cognitive",
    "economia conductual": "behavioral economics",
    "confianza e intuicion": "confidence and intuition",
}


def normalize_topic_key(tema: str) -> str:
    t = unicodedata.normalize("NFD", tema.lower().strip())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t)


def lookup_translation(tema: str) -> Optional[str]:
    return TOPIC_TRANSLATIONS.get(normalize_topic_key(tema))


def translate_topics_for_search(
    temas: list[str],
    llm: Optional[LLMClient] = None,
) -> dict[str, str]:
    """Devuelve mapa tema original → query en inglés para Unsplash."""
    queries: dict[str, str] = {}
    pending: list[str] = []

    for tema in temas:
        found = lookup_translation(tema)
        if found:
            queries[tema] = found
        else:
            pending.append(tema)

    if pending and llm is not None:
        queries.update(_translate_with_llm(pending, llm))
    else:
        for tema in pending:
            queries[tema] = tema

    return queries


def _translate_with_llm(temas: list[str], llm: LLMClient) -> dict[str, str]:
    lista = "\n".join(f"- {t}" for t in temas)
    prompt = f"""Traduce estos temas de un libro (español) a consultas cortas en inglés para buscar fotos explicativas en Unsplash.
Usa 2-4 palabras por tema, términos concretos y visuales (sin añadir infographic/illustration/chart; se agregan después).

Temas:
{lista}

Responde SOLO con JSON válido: {{"tema original exacto": "english search query", ...}}"""

    try:
        raw = llm.call(prompt)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
            if isinstance(parsed, dict):
                return {
                    tema: str(parsed.get(tema, tema)).strip()[:80]
                    for tema in temas
                }
    except Exception:
        pass

    return {tema: tema for tema in temas}


VISUAL_MARKERS = ("infographic", "illustration", "chart", "diagram", "visual")


def add_visual_suffix(query_en: str) -> str:
    """Añade un sufijo visual para obtener imágenes explicativas en Unsplash."""
    q = query_en.lower().strip()
    if any(marker in q for marker in VISUAL_MARKERS):
        return query_en.strip()

    if any(w in q for w in ("decision", "econom", "judgment", "heuristic")):
        suffix = "chart"
    elif any(w in q for w in ("behavior", "human", "emotion", "memory", "confidence")):
        suffix = "illustration"
    else:
        suffix = "infographic"

    return f"{query_en.strip()} {suffix}"

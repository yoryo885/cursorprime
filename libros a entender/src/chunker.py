"""
chunker.py — divide el texto del PDF en fragmentos coherentes y los rankea por tema.
"""
import re


def split_by_sentences(text: str, max_chars: int = 1500) -> list[str]:
    """Divide el texto en chunks respetando oraciones completas."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks


def rank_chunks_by_keywords(
    chunks: list[str],
    tema: str,
    top_n: int = 5,
) -> list[str]:
    """Selecciona los chunks más relevantes para el tema."""
    keywords = tema.lower().split()

    def score(chunk: str) -> float:
        chunk_lower = chunk.lower()
        keyword_hits = sum(chunk_lower.count(kw) for kw in keywords)
        length_bonus = min(len(chunk) / 500, 1.0)
        if len(chunk) < 200:
            return keyword_hits * 0.3 + length_bonus * 0.1
        return keyword_hits + length_bonus

    scored = sorted(chunks, key=score, reverse=True)
    return scored[:top_n]


# Alias retrocompatible
def build_chunks(text: str, chunk_size: int = 1500) -> list[str]:
    return split_by_sentences(text, max_chars=chunk_size)

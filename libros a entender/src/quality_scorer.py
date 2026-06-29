"""
quality_scorer.py — evalúa automáticamente cada resumen.
"""
from dataclasses import dataclass

from src.models import TopicResult


@dataclass
class QualityScore:
    tema: str
    score: float
    flags: list[str]
    passed: bool


class QualityScorer:
    MIN_WORDS = 120
    MAX_ENGLISH_RATIO = 0.08

    ENGLISH_MARKERS = {
        "the", "is", "are", "and", "this", "that", "with",
        "for", "was", "has", "have", "been", "not", "but",
        "from", "they", "their", "which", "will", "would",
    }

    SEGUNDA_PERSONA = [
        " tu ", " tus ", " te ", " ti ", " contigo",
        "puedes", "notarás", "entenderás", "descubrirás", "verás",
        "identificas", "priorizas", "revisas", "aprendes", "entiendes",
        "llevas", "haces", "tienes", "encuentras", "descubres",
        "¿cuánto tiempo llevas", "¿qué pasaría si",
    ]

    PRIMERA_PERSONA_PROHIBIDA = [
        " aprendí", " entiendo", " noto", " me doy cuenta", " yo ",
        " mi ", " mis ", " me ", " llevo ", " hago ",
    ]

    def score(self, result: TopicResult) -> QualityScore:
        flags: list[str] = []
        scores: list[float] = []

        words = result.resumen.split()
        total_words = max(len(words), 1)

        length_score = min(total_words / self.MIN_WORDS, 1.0)
        if length_score < 0.6:
            flags.append(f"resumen_corto: {total_words} palabras (mín {self.MIN_WORDS})")
        scores.append(length_score)

        english_count = sum(1 for w in words if w.lower() in self.ENGLISH_MARKERS)
        english_ratio = english_count / total_words
        lang_score = max(0.0, 1.0 - english_ratio / self.MAX_ENGLISH_RATIO)
        if lang_score < 0.7:
            flags.append(f"mezcla_idiomas: {english_ratio:.1%} inglés detectado")
        scores.append(lang_score)

        texto_lower = f" {result.resumen.lower()} "
        tiene_segunda = any(p in texto_lower for p in self.SEGUNDA_PERSONA)
        tiene_yo = any(p in texto_lower for p in self.PRIMERA_PERSONA_PROHIBIDA)
        persona_score = 1.0 if tiene_segunda and not tiene_yo else 0.35
        if not tiene_segunda:
            flags.append("falta_segunda_persona: no se detecta voz en «tú»")
        if tiene_yo:
            flags.append("mezcla_primera_persona: aparece yo/mi/me en el resumen")
        scores.append(persona_score)

        coverage_score = min(len(result.fragmentos) / 3, 1.0)
        if coverage_score < 0.5:
            flags.append(f"pocos_fragmentos: {len(result.fragmentos)} (mín 3)")
        scores.append(coverage_score)

        final = round(sum(scores) / len(scores), 2)
        passed = final >= 0.65 and len(flags) <= 1

        return QualityScore(tema=result.tema, score=final, flags=flags, passed=passed)

    def score_all(self, results: list[TopicResult]) -> dict:
        scores = [self.score(r) for r in results]
        book_score = round(sum(s.score for s in scores) / max(len(scores), 1), 2)
        fallidos = [s for s in scores if not s.passed]

        return {
            "book_score": book_score,
            "passed": len(fallidos) == 0,
            "topics": [vars(s) for s in scores],
            "failed_topics": [s.tema for s in fallidos],
            "summary": f"{len(scores) - len(fallidos)}/{len(scores)} temas aprobados",
        }

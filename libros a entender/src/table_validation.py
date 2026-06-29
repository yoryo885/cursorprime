"""Validación de celdas de tablas editoriales (truncado, escenarios repetidos)."""
from __future__ import annotations

import re

TERMINAL_PUNCT = frozenset(".!?…\"'»")

_WORD_NUMBERS: dict[str, int] = {
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "quince": 15,
    "veinte": 20,
    "treinta": 30,
}

MIN_WORDS = {
    "idea_clave": 8,
    "ejemplo_practico": 20,
    "aplicacion_vida_real": 15,
}


def text_looks_truncated(text: str, *, min_chars: int = 20) -> bool:
    """Detecta texto cortado a mitad de palabra u oración."""
    t = (text or "").strip()
    if len(t) < min_chars:
        return True
    if t.endswith("..."):
        return False
    if t[-1] in TERMINAL_PUNCT:
        return False

    words = t.split()
    if not words:
        return True

    last_word = words[-1].strip("\",'»")
    if len(last_word) <= 3:
        return True
    if len(last_word) < 7:
        return True
    if len(last_word) <= 10 and re.search(r"[^aeiouáéíóúy]{2,}$", last_word.lower()):
        return True
    return False


def extract_scenario_signature(text: str) -> str | None:
    """Firma numérica de escenario (p. ej. «5 de 30 estudiantes»)."""
    t = (text or "").lower()
    nums = [int(n) for n in re.findall(r"\b(\d+)\b", t)]
    if len(nums) >= 2:
        return f"{nums[0]}_{nums[1]}"

    found: list[int] = []
    for word, val in _WORD_NUMBERS.items():
        if re.search(rf"\b{word}\b", t):
            found.append(val)
    if len(found) >= 2:
        return f"{found[0]}_{found[1]}"
    if len(found) == 1:
        if re.search(r"\btreinta\b", t):
            return f"{found[0]}_30"
        if re.search(r"\bveinte\b", t):
            return f"{found[0]}_20"
    return None


def collect_used_scenarios(ejemplos: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for ejemplo in ejemplos:
        sig = extract_scenario_signature(ejemplo)
        if sig and sig not in seen:
            seen.add(sig)
            ordered.append(sig)
    return ordered


def ejemplo_reuses_scenario(text: str, ejemplos_anteriores: list[str]) -> bool:
    sig = extract_scenario_signature(text)
    if not sig:
        return False
    for prev in ejemplos_anteriores:
        if extract_scenario_signature(prev) == sig:
            return True
    return False


def build_scenario_dedup_hint(ejemplos_anteriores: list[str]) -> str:
    sigs = collect_used_scenarios(ejemplos_anteriores)
    if not sigs:
        return ""
    readable = ", ".join(s.replace("_", " de ") for s in sigs)
    return (
        f"- Escenarios numéricos ya usados (elige otras cifras): {readable}. "
        "Varía: 3 de 24, 4 de 18, 7 de 22, 8 casos de 45…"
    )


def validate_celda(text: str, campo: str) -> list[str]:
    issues: list[str] = []
    t = (text or "").strip()
    if not t or t in {"—", "-", "n/a"}:
        issues.append(f"{campo} vacío")
        return issues
    if text_looks_truncated(t):
        issues.append(f"{campo} truncado")
    min_w = MIN_WORDS.get(campo, 8)
    words = len(t.split())
    if words < min_w:
        issues.append(f"{campo} muy corto ({words} palabras)")
    return issues


def celda_es_valida(text: str, campo: str) -> bool:
    return not validate_celda(text, campo)

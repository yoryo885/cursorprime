"""Persistencia de introducciones por tema (ancladas a la audiencia/oficio)."""
from __future__ import annotations

import json
from pathlib import Path

from src.models import TopicResult
from src.output_paths import meta_dir

INTROS_FILENAME = "intros_tema.json"


def intros_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / INTROS_FILENAME


def save_topic_intros(
    output_dir: Path,
    intros: dict[str, str],
    *,
    audiencia: str = "",
) -> Path:
    path = intros_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"audiencia": audiencia, "intros": intros}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def load_topic_intros(output_dir: Path) -> tuple[dict[str, str], str]:
    path = intros_path(output_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        intros = {str(k): str(v) for k, v in data.get("intros", {}).items() if v}
        return intros, str(data.get("audiencia", "") or "")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}, ""


def apply_topic_intros(resultados: list[TopicResult], intros: dict[str, str]) -> None:
    for r in resultados:
        if r.tema in intros:
            r.intro_tema = intros[r.tema]

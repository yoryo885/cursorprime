"""
CheckpointManager — guarda el progreso tema a tema.
"""
import json
from pathlib import Path

from src.models import TopicResult


class CheckpointManager:
    def __init__(self, output_dir: Path):
        from src.output_paths import checkpoint_path

        self.path = checkpoint_path(output_dir)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, completed: list[TopicResult]) -> None:
        self.path.write_text(
            json.dumps([self._to_dict(r) for r in completed], ensure_ascii=False, indent=2)
        )

    def load(self) -> list[TopicResult]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text())
            return [TopicResult(**r) for r in data]
        except (json.JSONDecodeError, TypeError):
            print("⚠️  Checkpoint corrupto — empezando desde cero.")
            return []

    def done_topics(self) -> set[str]:
        return {r.tema for r in self.load()}

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

    @staticmethod
    def _to_dict(r: TopicResult) -> dict:
        return {
            "tema": r.tema,
            "resumen": r.resumen,
            "resumen_voz": r.resumen_voz,
            "fragmentos": r.fragmentos,
            "fallo": r.fallo,
            "intentos": r.intentos,
            "quality_score": r.quality_score,
            "quality_flags": r.quality_flags,
        }

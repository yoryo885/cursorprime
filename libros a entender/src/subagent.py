"""
subagent.py — procesa cada tema con checkpoint y control de calidad.
"""
from dataclasses import dataclass
from pathlib import Path

from src.checkpoint import CheckpointManager
from src.chunker import rank_chunks_by_keywords
from src.models import TopicResult
from src.quality_scorer import QualityScorer


@dataclass
class SubagentTask:
    temas: list[str]
    chunks: list[str]
    libro: str
    audiencia: str = ""
    reto_audiencia: str = ""
    intento_fallido_audiencia: str = ""


class Subagent:
    MAX_INTENTOS = 2

    def __init__(self, task: SubagentTask, llm, output_dir: Path, learning=None):
        self.task = task
        self.llm = llm
        self._chunks = task.chunks
        self.output_dir = output_dir
        self.learning = learning
        self.scorer = QualityScorer()

    def run(self) -> list[TopicResult]:
        checkpoint = CheckpointManager(self.output_dir)
        ya_hechos = checkpoint.done_topics()
        completados: list[TopicResult] = checkpoint.load()
        mejoras_prompt = self.learning.bloque_prompt() if self.learning else ""

        for tema in self.task.temas:
            if tema in ya_hechos:
                print(f"  ✓ '{tema}' ya procesado — saltando")
                continue

            result = self._procesar_tema(tema, mejoras_prompt, intento=1)

            qs = self.scorer.score(result)
            if not qs.passed and not result.fallo:
                print(f"  ⚠️  '{tema}' calidad baja ({qs.score}) — reintentando...")
                result = self._procesar_tema(tema, mejoras_prompt, intento=2)
                result.intentos = 2

            qs_final = self.scorer.score(result)
            result.quality_score = qs_final.score
            result.quality_flags = qs_final.flags

            completados.append(result)
            checkpoint.save(completados)
            estado = "✅" if qs_final.passed else "⚠️ "
            print(f"  {estado} '{tema}' guardado (score {qs_final.score})")

        checkpoint.clear()
        return completados

    def _procesar_tema(
        self, tema: str, mejoras_prompt: str, intento: int
    ) -> TopicResult:
        try:
            candidatos = rank_chunks_by_keywords(self._chunks, tema, top_n=5)
            extra = self._compose_extra_instructions(mejoras_prompt)
            fragmentos, resumen = self.llm.analyze_topic(
                tema=tema,
                chunks=candidatos,
                libro_nombre=self.task.libro,
                extra_instructions=extra,
                intento=intento,
            )
            return TopicResult(
                tema=tema,
                resumen=resumen,
                fragmentos=fragmentos,
                fallo=False,
                intentos=intento,
            )
        except Exception as exc:
            print(f"  ❌ Error procesando '{tema}': {exc}")
            return TopicResult(
                tema=tema,
                resumen="",
                fragmentos=[],
                fallo=True,
                intentos=intento,
            )

    def _compose_extra_instructions(self, mejoras_prompt: str) -> str:
        from src.audiencia_context import build_resumen_audiencia_instructions

        parts = []
        if self.task.audiencia:
            parts.append(
                build_resumen_audiencia_instructions(
                    {
                        "audiencia": self.task.audiencia,
                        "reto": self.task.reto_audiencia,
                        "intento_fallido": self.task.intento_fallido_audiencia,
                    },
                    output_dir=self.output_dir,
                )
            )
        if mejoras_prompt:
            parts.append(mejoras_prompt.strip())
        return "\n\n".join(p for p in parts if p)

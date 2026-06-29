"""
main_agent.py — orquestador principal del sistema.
"""
import json
from pathlib import Path
from typing import Optional

from src.chunker import split_by_sentences
from src.learning_agent import LearningSystem
from src.models import BookJob, ProcessingOutput, TopicResult
from src.quality_scorer import QualityScorer
from src.subagent import Subagent, SubagentTask


class MainAgent:
    def __init__(self, max_subagentes: int = 4):
        self.max_subagentes = max_subagentes
        self.scorer = QualityScorer()

    def process_book(self, job: BookJob) -> ProcessingOutput:
        from src.config import RESUMENES_DIR
        from src.output_paths import ensure_book_dirs, quality_report_path

        output_dir = RESUMENES_DIR / job.libro_slug
        ensure_book_dirs(output_dir)

        logs_dir = Path("logs")
        learning = LearningSystem(logs_dir)

        instrucciones = learning.instrucciones_activas()
        if instrucciones:
            print(f"📚 Aplicando {len(instrucciones)} mejoras de libros anteriores")

        if job.solo_enriquecer:
            return self._process_enrich_only(job, output_dir, learning)

        if job.solo_resumenes:
            return self._process_solo_resumenes(job, output_dir, learning)

        llm = self._ensure_llm(job)
        pdf_text = self._extract_pdf_text(job.pdf_path)

        chunks = split_by_sentences(pdf_text, max_chars=1500)
        print(f"📄 PDF dividido en {len(chunks)} fragmentos")

        print(f"📚 Procesando: {job.libro_slug}")
        print(f"   Temas: {len(job.temas)}")
        resultados = self._ejecutar_subagentes(job, chunks, llm, output_dir, learning)
        resultados.sort(key=lambda r: job.temas.index(r.tema))

        resultados = self._corregir(resultados, llm, output_dir)
        for r in resultados:
            if not r.fallo and r.resumen.strip():
                r.resumen_voz = r.resumen

        quality = self._evaluar_y_reintentar(resultados, llm, output_dir, job)

        quality_report_path(output_dir).write_text(
            json.dumps(quality, ensure_ascii=False, indent=2)
        )
        print(f"\n📊 Calidad del libro: {quality['book_score']} — {quality['summary']}")

        from datetime import datetime
        from src.output import write_book_summary
        from src.pdf_reader import get_book_name

        libro_nombre = get_book_name(Path(job.pdf_path))
        write_book_summary(libro_nombre, resultados, output_dir, datetime.now())

        package = self._run_enrichment(
            job, resultados, output_dir, libro_nombre=libro_nombre
        )
        self._registrar_aprendizaje(learning, quality, resultados, job.libro_slug)
        learning.validar(quality["book_score"])

        return ProcessingOutput(
            libro_slug=job.libro_slug,
            resultados=resultados,
            output_dir=str(output_dir),
            quality_report=quality,
            markdown_path=getattr(package, "markdown_path", None),
            pdf_path=getattr(package, "pdf_path", None),
            package=package,
        )

    def _ejecutar_subagentes(
        self,
        job: BookJob,
        chunks: list[str],
        llm,
        output_dir: Path,
        learning: LearningSystem,
    ) -> list[TopicResult]:
        from src.audiencia_context import load_audiencia_context

        aud_ctx = load_audiencia_context(output_dir)
        if aud_ctx.get("audiencia"):
            from src.rol_usuario import ensure_rol_perfil

            profile = ensure_rol_perfil(output_dir)
            familia = f" · {profile.familia_rol}" if profile else ""
            print(f"   📌 ROL_USUARIO: {aud_ctx['audiencia']}{familia}")

        task = SubagentTask(
            temas=job.temas,
            chunks=chunks,
            libro=job.libro_slug,
            audiencia=aud_ctx.get("audiencia", ""),
            reto_audiencia=aud_ctx.get("reto", ""),
            intento_fallido_audiencia=aud_ctx.get("intento_fallido", ""),
        )
        return Subagent(task, llm, output_dir, learning=learning).run()

    def _corregir(self, resultados: list[TopicResult], llm, output_dir: Optional[Path] = None) -> list[TopicResult]:
        try:
            from src.text_corrector import TextCorrector
            return TextCorrector(llm).correct_all(resultados, output_dir=output_dir)
        except ImportError:
            print("⚠️  TextCorrector no disponible — saltando corrección")
            return resultados

    def _evaluar_y_reintentar(
        self,
        resultados: list[TopicResult],
        llm,
        output_dir: Path,
        job: BookJob,
    ) -> dict:
        quality = self.scorer.score_all(resultados)

        if quality["failed_topics"]:
            print(f"\n⚠️  Reintentando {len(quality['failed_topics'])} temas con baja calidad...")
            chunks = split_by_sentences(self._extract_pdf_text(job.pdf_path), max_chars=1500)
            for tema in quality["failed_topics"]:
                nuevo = self._retry_topic(tema, resultados, llm, chunks, output_dir)
                resultados[:] = [nuevo if r.tema == tema else r for r in resultados]
            quality = self.scorer.score_all(resultados)

        return quality

    def _retry_topic(
        self,
        tema: str,
        resultados: list[TopicResult],
        llm,
        chunks: list[str],
        output_dir: Path,
    ) -> TopicResult:
        try:
            from src.audiencia_context import (
                build_resumen_audiencia_instructions,
                load_audiencia_context,
            )
            from src.chunker import rank_chunks_by_keywords

            aud_ctx = load_audiencia_context(output_dir)
            audiencia_block = build_resumen_audiencia_instructions(aud_ctx, output_dir=output_dir)
            candidatos = rank_chunks_by_keywords(chunks, tema, top_n=5)
            extra_parts = [
                audiencia_block,
                "Segundo intento: escribe al menos 150 palabras en segunda persona "
                "(notarás, descubrirás, tu trabajo, identificas, entiendes).",
            ]
            fragmentos, resumen = llm.analyze_topic(
                tema=tema,
                chunks=candidatos,
                libro_nombre="",
                extra_instructions="\n\n".join(p for p in extra_parts if p),
                intento=2,
            )
            nuevo = TopicResult(
                tema=tema,
                resumen=resumen,
                fragmentos=fragmentos,
                fallo=False,
                intentos=2,
            )
            qs = self.scorer.score(nuevo)
            nuevo.quality_score = qs.score
            nuevo.quality_flags = qs.flags
            print(f"  🔄 '{tema}' reintentado → score {qs.score}")
            return nuevo
        except Exception as exc:
            print(f"  ❌ Reintento fallido para '{tema}': {exc}")
            original = next((r for r in resultados if r.tema == tema), None)
            return original or TopicResult(tema=tema, fallo=True)

    def _registrar_aprendizaje(
        self,
        learning: LearningSystem,
        quality: dict,
        resultados: list[TopicResult],
        libro: str,
    ) -> None:
        flag_counts: dict[str, int] = {}
        for r in resultados:
            for flag in r.quality_flags:
                clave = flag.split(":")[0]
                flag_counts[clave] = flag_counts.get(clave, 0) + 1

        instrucciones_map = {
            "resumen_corto": (
                "Escribe resúmenes de al menos 150 palabras por tema. "
                "Desarrolla cada idea con ejemplos del texto."
            ),
            "mezcla_idiomas": (
                "El resumen debe estar completamente en español. "
                "No uses palabras ni frases en inglés."
            ),
            "falta_segunda_persona": (
                "Escribe el resumen en segunda persona directa: tú, tu, tus, te. "
                "Usa notarás, descubrirás, identificas, entiendes, tu trabajo."
            ),
            "mezcla_primera_persona": (
                "Elimina primera persona (yo, mi, me, aprendí). "
                "Reescribe todo hablando al lector en «tú»."
            ),
            "falta_primera_persona": (
                "Escribe en segunda persona: tú, tu, tus. Prohibido yo/mi/me."
            ),
            "pocos_fragmentos": (
                "Apóyate en al menos 3 fragmentos distintos del texto para cada tema."
            ),
        }

        for flag_clave, count in flag_counts.items():
            if count >= 2 and flag_clave in instrucciones_map:
                learning.registrar(
                    instruccion=instrucciones_map[flag_clave],
                    libro=libro,
                    score_antes=quality["book_score"],
                )

        for r in resultados:
            if r.fallo:
                learning.registrar_error(r.tema, libro, "fallo_completo")
            elif r.quality_score < 0.5:
                learning.registrar_error(r.tema, libro, f"score_bajo_{r.quality_score}")

    def _process_solo_resumenes(
        self, job: BookJob, output_dir: Path, learning: LearningSystem
    ) -> ProcessingOutput:
        """Regenera solo los resúmenes por tema (anclados a audiencia si hay plan)."""
        from datetime import datetime

        from src.agents.book_package import BookPackage
        from src.checkpoint import CheckpointManager
        from src.md_loader import find_summary_md, parse_enriched_markdown
        from src.output import write_book_summary
        from src.output_paths import quality_report_path
        from src.pdf_reader import get_book_name
        from src.tablas_store import resolve_tablas

        llm = self._ensure_llm(job)
        md_path = find_summary_md(output_dir)
        libro_nombre, _, tablas_md, _ = parse_enriched_markdown(md_path)
        tablas = resolve_tablas(output_dir, tablas_md)

        if job.temas:
            temas_list = job.temas
        else:
            temas_list = [r.tema for r in parse_enriched_markdown(md_path)[1]]
            if not temas_list:
                try:
                    plan_data = json.loads(
                        (output_dir / "meta" / "plan.json").read_text(encoding="utf-8")
                    )
                    temas_list = plan_data.get("temas", [])
                except (FileNotFoundError, json.JSONDecodeError, OSError):
                    pass

        if not temas_list:
            raise ValueError(
                f"No hay temas en {output_dir} — indica temas en CLI o genera el libro primero."
            )

        job.temas = temas_list
        CheckpointManager(output_dir).clear()

        pdf_text = self._extract_pdf_text(job.pdf_path)
        chunks = split_by_sentences(pdf_text, max_chars=1500)
        print(f"📝 Solo resúmenes: {len(temas_list)} temas → audiencia del plan")

        resultados = self._ejecutar_subagentes(job, chunks, llm, output_dir, learning)
        resultados.sort(key=lambda r: job.temas.index(r.tema))
        resultados = self._corregir(resultados, llm, output_dir)
        for r in resultados:
            if not r.fallo and r.resumen.strip():
                r.resumen_voz = r.resumen

        quality = self._evaluar_y_reintentar(resultados, llm, output_dir, job)
        quality_report_path(output_dir).write_text(
            json.dumps(quality, ensure_ascii=False, indent=2)
        )

        package = BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=job.libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas,
        )
        write_book_summary(
            libro_nombre or get_book_name(Path(job.pdf_path)),
            resultados,
            output_dir,
            datetime.now(),
            package=package,
        )
        print(f"\n✅ Resúmenes actualizados en {output_dir}")
        return ProcessingOutput(
            libro_slug=job.libro_slug,
            resultados=resultados,
            output_dir=str(output_dir),
            quality_report=quality,
            markdown_path=find_summary_md(output_dir),
        )

    def _process_enrich_only(
        self, job: BookJob, output_dir: Path, learning: LearningSystem
    ) -> ProcessingOutput:
        from src.md_loader import find_summary_md, parse_enriched_markdown
        md_path = find_summary_md(output_dir)
        libro, resultados, tablas, _ = parse_enriched_markdown(md_path)
        print(f"⚡ Solo enriquecer: {libro}")
        package = self._run_enrichment(
            job, resultados, output_dir, libro_nombre=libro, tablas_existentes=tablas
        )
        return ProcessingOutput(
            libro_slug=job.libro_slug,
            resultados=resultados,
            output_dir=str(output_dir),
            markdown_path=getattr(package, "markdown_path", None),
            pdf_path=getattr(package, "pdf_path", None),
            package=package,
        )

    def _run_enrichment(
        self,
        job: BookJob,
        resultados: list[TopicResult],
        output_dir: Path,
        libro_nombre: str = "",
        tablas_existentes: Optional[list] = None,
    ):
        try:
            from src.pipeline import PostProcessingPipeline
            llm = self._ensure_llm(job) if not job.sin_llm else None
            print("   🚀 Pipeline de enriquecimiento...")
            return PostProcessingPipeline(
                llm,
                sin_llm=job.sin_llm,
                sin_imagenes=job.sin_imagenes,
                sin_md=job.sin_md,
                solo_mapa=job.solo_mapa,
                solo_tablas=job.solo_tablas,
                solo_pdf=job.solo_pdf,
                solo_intros=job.solo_intros,
                solo_plan_accion=job.solo_plan_accion,
                sin_qc=job.sin_qc,
            ).run(
                resultados,
                job.libro_slug,
                output_dir,
                temas=job.temas or [r.tema for r in resultados],
                libro_nombre=libro_nombre,
                tablas_existentes=tablas_existentes,
            )
        except ImportError as exc:
            print(f"⚠️  PostProcessingPipeline no disponible — {exc}")
            return None

    def _ensure_llm(self, job: BookJob):
        if job.sin_llm:
            return None
        from src.config import ANTHROPIC_API_KEY
        from src.llm import LLMClient
        if not ANTHROPIC_API_KEY:
            raise ValueError("Se requiere ANTHROPIC_API_KEY en .env")
        return LLMClient(ANTHROPIC_API_KEY)

    def _extract_pdf_text(self, pdf_path: str) -> str:
        from src.pdf_reader import extract_text
        return extract_text(pdf_path)

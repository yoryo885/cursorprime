"""
pipeline.py — adaptador del pipeline visual (tablas, mapa, imágenes, PDF).
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.agents.pipeline import PostProcessingPipeline as AgentPipeline
from src.context_agent import ContextAgent
from src.learning import LearningSystem as LegacyLearning
from src.md_loader import find_summary_md, parse_enriched_markdown
from src.output import write_book_summary


class PostProcessingPipeline:
    def __init__(self, llm, sin_llm: bool = False, sin_imagenes: bool = False, sin_md: bool = False, solo_mapa: bool = False, solo_tablas: bool = False, solo_pdf: bool = False, solo_intros: bool = False, solo_plan_accion: bool = False, sin_qc: bool = False):
        self.llm = llm
        self.sin_llm = sin_llm
        self.sin_imagenes = sin_imagenes
        self.sin_md = sin_md
        self.solo_mapa = solo_mapa
        self.solo_tablas = solo_tablas
        self.solo_pdf = solo_pdf
        self.solo_intros = solo_intros
        self.solo_plan_accion = solo_plan_accion
        self.sin_qc = sin_qc
        self._inner = AgentPipeline(llm, LegacyLearning())

    def run(
        self,
        resultados: list,
        libro_slug: str,
        output_dir: Path,
        temas: Optional[list] = None,
        libro_nombre: str = "",
        tablas_existentes: Optional[list] = None,
    ):
        output_dir = Path(output_dir)
        temas = temas or [r.tema for r in resultados]

        if not libro_nombre or tablas_existentes is None:
            try:
                md_path = find_summary_md(output_dir)
                libro_nombre, _, tablas_md, _ = parse_enriched_markdown(md_path)
                tablas_existentes = tablas_existentes if tablas_existentes is not None else tablas_md
            except FileNotFoundError:
                libro_nombre = libro_nombre or libro_slug
                tablas_existentes = tablas_existentes or []

        fecha = datetime.now()
        contexto_usuario = ContextAgent.recopilar(
            output_dir.name,
            output_dir,
            llm=self.llm,
            resultados=resultados,
        )
        self._inner._contexto_usuario = contexto_usuario
        package = self._inner.run(
            resultados=resultados,
            temas=temas,
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            fecha=fecha,
            sin_llm=self.sin_llm,
            sin_imagenes=self.sin_imagenes,
            tablas_existentes=tablas_existentes,
            solo_mapa=self.solo_mapa,
            solo_tablas=self.solo_tablas,
            solo_pdf=self.solo_pdf,
            solo_intros=self.solo_intros,
            solo_plan_accion=self.solo_plan_accion,
            sin_qc=self.sin_qc,
        )
        if not self.sin_md:
            md_path = write_book_summary(
                libro_nombre, resultados, output_dir, fecha, package
            )
            package.markdown_path = md_path
        else:
            print("   ⏭️  Markdown: no regenerado")
        return package

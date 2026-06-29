from datetime import datetime
import json
from pathlib import Path
from typing import Optional

from src.agents.book_package import BookPackage
from src.agents.images_agent import ImagesAgent
from src.agents.learning_agent import LearningAgent
from src.agents.map_agent import MapAgent
from src.agents.pdf_design_agent import PDFDesignAgent, load_or_create_intro
from src.agents.audience_intro_agent import AudienceIntroAgent
from src.agents.tables_agent import TablesAgent
from src.agents.topic_intro_agent import resolve_audiencia
from src.learning import LearningSystem
from src.llm import LLMClient
from src.models import TopicResult


class PostProcessingPipeline:
    """
    Pipeline post-resumen:
    tablas (Claude + HTML/CSS + Playwright) → mapa (Claude + HTML/CSS + Playwright) → imágenes → PDF → aprendizaje
    """

    def __init__(self, llm: Optional[LLMClient], learning: LearningSystem):
        self.llm = llm
        self.learning = learning
        self._contexto_usuario: dict | None = None
        self._sin_qc = False

    def run(
        self,
        resultados: list[TopicResult],
        temas: list[str],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        sin_llm: bool = False,
        sin_imagenes: bool = False,
        sin_qc: bool = False,
        tablas_existentes: Optional[list] = None,
        solo_mapa: bool = False,
        solo_tablas: bool = False,
        solo_pdf: bool = False,
        solo_intros: bool = False,
        solo_plan_accion: bool = False,
    ) -> BookPackage:
        self._sin_qc = sin_qc
        prompts = self.learning.load_all_prompts()
        tablas_existentes = tablas_existentes or []

        if solo_plan_accion:
            return self._run_solo_plan_accion(
                resultados=resultados,
                libro_nombre=libro_nombre,
                libro_slug=libro_slug,
                output_dir=output_dir,
                fecha=fecha,
                tablas_existentes=tablas_existentes,
                sin_qc=sin_qc,
            )

        if solo_pdf:
            return self._run_solo_pdf(
                resultados=resultados,
                libro_nombre=libro_nombre,
                libro_slug=libro_slug,
                output_dir=output_dir,
                fecha=fecha,
                tablas_existentes=tablas_existentes,
                sin_qc=sin_qc,
            )

        if solo_intros:
            return self._run_solo_intro_audiencia(
                resultados=resultados,
                libro_nombre=libro_nombre,
                libro_slug=libro_slug,
                output_dir=output_dir,
                fecha=fecha,
                tablas_existentes=tablas_existentes,
            )

        if solo_tablas:
            return self._run_solo_tablas(
                resultados=resultados,
                libro_nombre=libro_nombre,
                libro_slug=libro_slug,
                output_dir=output_dir,
                fecha=fecha,
                prompts=prompts,
            )

        if solo_mapa:
            return self._run_solo_mapa(
                resultados=resultados,
                temas=temas,
                libro_nombre=libro_nombre,
                libro_slug=libro_slug,
                output_dir=output_dir,
                fecha=fecha,
                tablas_existentes=tablas_existentes,
                prompts=prompts,
            )

        tablas_ok = [
            t for t in tablas_existentes
            if t.image_path
            and Path(t.image_path).exists()
            and Path(t.image_path).suffix.lower() == ".png"
            and Path(t.image_path).stat().st_size > 5000
            and t.idea_clave
        ]
        tablas_map = {t.tema: t for t in tablas_ok}

        for r in resultados:
            if not r.fallo and r.resumen.strip() and not r.resumen_voz.strip():
                r.resumen_voz = r.resumen

        # 1. Tablas (Claude + HTML/CSS + Playwright)
        if sin_llm and tablas_ok:
            tablas = tablas_ok
            print(f"   ⏭️  Tablas: reutilizando {len(tablas)} existentes")
        elif sin_llm:
            tablas = []
        else:
            need_tablas = [r for r in resultados if not r.fallo and r.tema not in tablas_map]
            tablas = list(tablas_ok)
            if need_tablas:
                nuevas = TablesAgent(self.llm, prompts.get("tablas", [])).run(
                    need_tablas,
                    libro_nombre,
                    output_dir,
                    contexto_usuario=self._contexto_usuario,
                )
                tablas.extend(nuevas)
            else:
                print(f"   ⏭️  Tablas: reutilizando {len(tablas)} existentes")

        # 2. Mapa conceptual (Claude + HTML/CSS + Playwright)
        from src.output_paths import resolve_mapa_png

        mapa_path = resolve_mapa_png(output_dir)
        if sin_llm and mapa_path:
            print(f"   ⏭️  Mapa: reutilizando {mapa_path.relative_to(output_dir)}")
        elif sin_llm:
            mapa_path = None
        else:
            mapa_path = MapAgent(self.llm, prompts.get("mapa", [])).run(
                temas, libro_nombre, output_dir
            )

        # 3. Imágenes (Unsplash) — opcional
        if sin_imagenes:
            print("   ⏭️  Imágenes: omitidas")
            imagenes = {}
        else:
            imagenes = ImagesAgent(prompts.get("imagenes", []), llm=self.llm).run(
                resultados, libro_nombre, output_dir
            )

        introduccion = load_or_create_intro(output_dir, libro_nombre)
        self._ensure_audience_intro(output_dir, libro_nombre=libro_nombre, sin_llm=sin_llm)
        self._ensure_action_plan(
            resultados,
            tablas,
            output_dir=output_dir,
            libro_nombre=libro_nombre,
            sin_llm=sin_llm,
        )

        package = BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas,
            mapa_path=mapa_path if mapa_path and Path(mapa_path).exists() else None,
            imagenes=imagenes,
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=not sin_imagenes,
        )

        # 4. PDF (HTML + Playwright)
        pdf_ok = False
        try:
            PDFDesignAgent().run(package)
            pdf_ok = package.pdf_path is not None
        except Exception as err:
            print(f"   ⚠️  PDF Playwright falló: {err}")
            try:
                from src.md_pdf_export import build_pdf_from_markdown

                pdf_path = build_pdf_from_markdown(
                    output_dir,
                    libro_nombre=libro_nombre,
                    sin_imagenes_unsplash=sin_imagenes,
                )
                package.pdf_path = pdf_path
                pdf_ok = True
                print(f"   ✓ PDF fallback desde .md: {pdf_path.name}")
            except Exception as fallback_err:
                print(f"   ⚠️  PDF fallback falló: {fallback_err}")

        if pdf_ok and not sin_qc:
            self._run_final_qc(package, output_dir)

        # 5. Aprendizaje
        if not sin_llm:
            LearningAgent(self.learning).run(
                llm=self.llm,
                libro_slug=libro_slug,
                libro_nombre=libro_nombre,
                resultados=resultados,
                tablas_count=len(tablas),
                imagenes_count=len(imagenes),
                pdf_ok=pdf_ok,
            )

        return package

    def _run_solo_mapa(
        self,
        *,
        resultados: list[TopicResult],
        temas: list[str],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        tablas_existentes: list,
        prompts: dict,
    ) -> BookPackage:
        print("   🗺️  Modo solo mapa: Claude + HTML/CSS + Playwright")
        if not self.llm:
            raise ValueError("Se requiere ANTHROPIC_API_KEY para generar el mapa")

        mapa_path = MapAgent(self.llm, prompts.get("mapa", [])).run(
            temas, libro_nombre, output_dir, force=True
        )
        introduccion = load_or_create_intro(output_dir, libro_nombre)

        return BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas_existentes,
            mapa_path=mapa_path if mapa_path and Path(mapa_path).exists() else None,
            imagenes={},
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=False,
        )

    def _run_solo_tablas(
        self,
        *,
        resultados: list[TopicResult],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        prompts: dict,
    ) -> BookPackage:
        print("   📊 Modo solo tablas: voz Yordy + diseño iconos + Playwright")
        if not self.llm:
            raise ValueError("Se requiere ANTHROPIC_API_KEY para generar tablas")

        need = [r for r in resultados if not r.fallo]
        tablas = TablesAgent(self.llm, prompts.get("tablas", [])).run(
            need,
            libro_nombre,
            output_dir,
            force=True,
            contexto_usuario=self._contexto_usuario,
        )
        introduccion = load_or_create_intro(output_dir, libro_nombre)

        return BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas,
            mapa_path=None,
            imagenes={},
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=False,
        )

    def _run_solo_plan_accion(
        self,
        *,
        resultados: list[TopicResult],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        tablas_existentes: list,
        sin_qc: bool = False,
    ) -> BookPackage:
        print("   📋 Modo solo plan de acción + PDF")
        if not self.llm:
            raise ValueError("Se requiere ANTHROPIC_API_KEY para generar el plan de acción")

        from src.output_paths import resolve_mapa_png
        from src.tablas_store import resolve_tablas

        tablas_ok = resolve_tablas(output_dir, tablas_existentes)
        self._ensure_action_plan(
            resultados,
            tablas_ok,
            output_dir=output_dir,
            libro_nombre=libro_nombre,
            sin_llm=False,
            force=True,
        )
        introduccion = load_or_create_intro(output_dir, libro_nombre)
        mapa_path = resolve_mapa_png(output_dir)

        package = BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas_ok,
            mapa_path=mapa_path,
            imagenes={},
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=False,
        )
        PDFDesignAgent().run(package)
        if not sin_qc:
            self._run_final_qc(package, output_dir)
        return package

    def _run_solo_pdf(
        self,
        *,
        resultados: list[TopicResult],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        tablas_existentes: list,
        sin_qc: bool = False,
    ) -> BookPackage:
        print("   📄 Modo solo PDF: portada + mapa + temas + tablas iconos (HTML + Playwright)")
        introduccion = load_or_create_intro(output_dir, libro_nombre)
        from src.output_paths import resolve_mapa_png
        from src.tablas_store import resolve_tablas

        tablas_ok = resolve_tablas(output_dir, tablas_existentes)
        mapa_path = resolve_mapa_png(output_dir)
        self._ensure_audience_intro(output_dir, libro_nombre=libro_nombre, sin_llm=True)
        self._ensure_action_plan(
            resultados,
            tablas_ok,
            output_dir=output_dir,
            libro_nombre=libro_nombre,
            sin_llm=True,
        )

        package = BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=tablas_ok,
            mapa_path=mapa_path,
            imagenes={},
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=False,
        )

        PDFDesignAgent().run(package)
        if not sin_qc:
            self._run_final_qc(package, output_dir)
        return package

    def _run_solo_intro_audiencia(
        self,
        *,
        resultados: list[TopicResult],
        libro_nombre: str,
        libro_slug: str,
        output_dir: Path,
        fecha: datetime,
        tablas_existentes: list,
    ) -> BookPackage:
        print("   📌 Modo solo intro audiencia: para quién está hecho el resumen")
        if not self.llm:
            raise ValueError("Se requiere ANTHROPIC_API_KEY para generar intro audiencia")

        self._ensure_audience_intro(
            output_dir, libro_nombre=libro_nombre, sin_llm=False, force=True
        )
        introduccion = load_or_create_intro(output_dir, libro_nombre)
        from src.output_paths import resolve_mapa_png
        from src.tablas_store import resolve_tablas

        return BookPackage(
            libro_nombre=libro_nombre,
            libro_slug=libro_slug,
            output_dir=output_dir,
            resultados=resultados,
            tablas=resolve_tablas(output_dir, tablas_existentes),
            mapa_path=resolve_mapa_png(output_dir),
            imagenes={},
            introduccion=introduccion,
            fecha=fecha,
            incluir_imagenes_pdf=False,
        )

    def _ensure_audience_intro(
        self,
        output_dir: Path,
        *,
        libro_nombre: str,
        sin_llm: bool = False,
        force: bool = False,
    ) -> None:
        ctx = self._contexto_usuario or {}
        try:
            data = json.loads((Path(output_dir) / "contexto_usuario.json").read_text(encoding="utf-8"))
            ctx = {**ctx, **data}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

        audiencia = str(ctx.get("audiencia", "") or resolve_audiencia(output_dir, ctx))
        if sin_llm or not self.llm or not audiencia:
            return

        AudienceIntroAgent(self.llm).run(
            output_dir,
            libro_nombre=libro_nombre,
            audiencia=audiencia,
            reto=str(ctx.get("reto", "")),
            intento_fallido=str(ctx.get("intento_fallido", "")),
            force=force,
        )

    def _ensure_action_plan(
        self,
        resultados: list[TopicResult],
        tablas: list,
        *,
        output_dir: Path,
        libro_nombre: str,
        sin_llm: bool = False,
        force: bool = False,
    ) -> None:
        from src.agents.action_plan_agent import ActionPlanAgent

        if sin_llm and not force:
            return
        if not self.llm and not force:
            return

        ActionPlanAgent(self.llm).run(
            resultados,
            tablas,
            libro_nombre=libro_nombre,
            output_dir=output_dir,
            force=force,
        )

    def _run_final_qc(self, package: BookPackage, output_dir: Path) -> None:
        from src.agents.final_qc_agent import FinalQCAgent

        audiencia = ""
        try:
            ctx_path = Path(output_dir) / "contexto_usuario.json"
            if ctx_path.exists():
                ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
                audiencia = ctx.get("audiencia", "") or ctx.get("ocupacion", "")
            if not audiencia:
                from src.agents.planner_agent import plan_path_for, BookPlan

                plan_path = plan_path_for(output_dir)
                if plan_path.exists():
                    plan = BookPlan.from_dict(
                        json.loads(plan_path.read_text(encoding="utf-8"))
                    )
                    audiencia = plan.audiencia or plan.contexto_usuario.get("ocupacion", "")
        except Exception:
            pass

        FinalQCAgent(self.llm).run_with_auto_fix(
            package,
            audiencia=audiencia,
            contexto_usuario=self._contexto_usuario,
            skip_llm=self.llm is None,
            learning=self.learning,
        )

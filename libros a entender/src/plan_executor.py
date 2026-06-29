"""Ejecuta un BookPlan de punta a punta (un solo comando desde plan.py)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.agents.final_qc_agent import FinalQCAgent
from src.agents.planner_agent import BookPlan, PlannerAgent, _resolve_pdf
from src.config import RESUMENES_DIR
from src.models import BookJob, ProcessingOutput


@dataclass
class PlanProgress:
    resumenes: bool = False
    tablas: bool = False
    mapa: bool = False
    pdf: bool = False

    @property
    def completo(self) -> bool:
        return self.resumenes and self.tablas and self.mapa and self.pdf


def resolve_book_pdf(path_or_name: str) -> Path:
    """Resuelve ruta al PDF desde plan (nombre, ruta relativa o libros/*.pdf)."""
    candidate = _resolve_pdf(path_or_name)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"No se encontró el PDF «{path_or_name}» "
        f"(probado: {candidate} y libros/{Path(path_or_name).stem}.pdf)"
    )


class PlanExecutor:
    """Orquesta el pipeline editorial completo a partir de un plan guardado."""

    def __init__(
        self,
        plan: BookPlan,
        *,
        max_subagentes: int = 4,
        sin_imagenes: bool = False,
        sin_qc: bool = False,
        forzar: bool = False,
        desde: str = "auto",
    ):
        self.plan = plan
        self.max_subagentes = max_subagentes
        self.sin_imagenes = sin_imagenes
        self.sin_qc = sin_qc
        self.forzar = forzar
        self.desde = desde if desde in ("auto", "resumenes", "tablas", "pdf") else "auto"

    @classmethod
    def from_slug(cls, slug: str, **kwargs) -> PlanExecutor:
        return cls(PlannerAgent.load(RESUMENES_DIR / slug), **kwargs)

    @property
    def output_dir(self) -> Path:
        return RESUMENES_DIR / self.plan.libro_slug

    def progress(self) -> PlanProgress:
        from src.md_loader import find_summary_md, parse_enriched_markdown
        from src.output_paths import resolve_mapa_png
        from src.tablas_store import resolve_tablas

        out = PlanProgress()
        temas = self.plan.temas

        try:
            _, resultados, _, _ = parse_enriched_markdown(find_summary_md(self.output_dir))
            ok = {
                r.tema
                for r in resultados
                if not r.fallo and (r.resumen_voz or r.resumen).strip()
            }
            out.resumenes = all(t in ok for t in temas)
        except (FileNotFoundError, OSError):
            pass

        tablas = resolve_tablas(self.output_dir, [])
        tablas_ok = {
            t.tema for t in tablas if (t.idea_clave or "").strip() and t.ejemplo_practico
        }
        out.tablas = len(tablas_ok) >= len(temas)

        mapa = resolve_mapa_png(self.output_dir)
        out.mapa = mapa is not None and Path(mapa).exists()

        pdf = self._find_pdf()
        out.pdf = pdf is not None and pdf.stat().st_size >= FinalQCAgent.MIN_PDF_BYTES

        return out

    def _find_pdf(self) -> Path | None:
        for pdf in sorted(self.output_dir.glob("*.pdf")):
            if pdf.stat().st_size >= FinalQCAgent.MIN_PDF_BYTES:
                return pdf
        return None

    def _print_pasos(self, prog: PlanProgress) -> None:
        checks = [
            ("Resúmenes por tema", prog.resumenes),
            ("Intro audiencia + tablas", prog.tablas),
            ("Mapa conceptual", prog.mapa),
            ("PDF editorial", prog.pdf),
        ]
        print("\n▶ Pipeline desde plan:")
        for i, (label, done) in enumerate(checks, 1):
            estado = "✓ listo" if done else "→ pendiente"
            if self.forzar:
                estado = "↻ regenerar"
            print(f"   {i}. {label}: {estado}")
        for paso in self.plan.pasos[:6]:
            print(f"      · {paso}")

    def _build_job(self, pdf: Path, *, modo: str) -> BookJob:
        job = BookJob(
            pdf_path=str(pdf),
            temas=self.plan.temas,
            max_subagentes=self.max_subagentes,
            libro_slug=self.plan.libro_slug,
            sin_imagenes=self.sin_imagenes,
            sin_qc=self.sin_qc,
        )
        if modo == "enriquecer":
            job.solo_enriquecer = True
        elif modo == "pdf":
            job.solo_enriquecer = True
            job.solo_pdf = True
            job.sin_imagenes = True
            job.sin_md = True
        return job

    def _resolve_modo(self, prog: PlanProgress) -> str:
        if self.forzar or self.desde == "resumenes":
            return "completo"
        if self.desde == "tablas":
            if not prog.resumenes:
                raise FileNotFoundError(
                    "No hay resúmenes .md — ejecuta primero sin --desde tablas."
                )
            return "enriquecer"
        if self.desde == "pdf":
            if not prog.resumenes:
                raise FileNotFoundError("No hay resúmenes .md.")
            if not prog.tablas:
                raise FileNotFoundError("No hay tablas — usa --desde tablas primero.")
            return "pdf"
        if not prog.resumenes:
            return "completo"
        if not prog.tablas or not prog.mapa or not prog.pdf:
            return "enriquecer"
        return "pdf"

    def execute(self) -> ProcessingOutput:
        from src.main_agent import MainAgent

        pdf = resolve_book_pdf(self.plan.pdf_path or self.plan.libro_nombre)
        prog = self.progress()
        self._print_pasos(prog)

        modo = self._resolve_modo(prog)
        labels = {
            "completo": "Pipeline completo (resúmenes → tablas → mapa → PDF → QC)",
            "enriquecer": "Continuando (tablas / mapa / PDF / QC)",
            "pdf": "Solo PDF + QC (artefactos existentes)",
        }
        print(f"\n🚀 {labels[modo]}")

        job = self._build_job(pdf, modo=modo)
        output = MainAgent(max_subagentes=self.max_subagentes).process_book(job)
        self._print_resultado(output)
        return output

    @staticmethod
    def _print_resultado(output: ProcessingOutput) -> None:
        print(f"\n✅ Listo. Salida en: resumenes/{output.libro_slug}/")
        if output.markdown_path:
            print(f"✅ Markdown: {output.markdown_path}")
        if output.pdf_path and Path(output.pdf_path).exists():
            print(f"✅ PDF:      {output.pdf_path}")
        pkg = output.package
        if pkg and pkg.mapa_path and Path(pkg.mapa_path).exists():
            print(f"✅ Mapa:     {pkg.mapa_path}")
        qr = output.quality_report or {}
        if qr.get("book_score") is not None:
            print(f"📊 Calidad resúmenes: {qr.get('book_score')} — {qr.get('summary', '')}")

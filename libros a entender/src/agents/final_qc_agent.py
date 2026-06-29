"""Agente de control de calidad final: tablas + PDF antes del entregable."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from src.agents.book_package import BookPackage, TopicTable
from src.agents.table_subagents import collect_used_protagonists
from src.output_paths import final_qc_report_path, resolve_mapa_png, tablas_dir
from src.quality_scorer import QualityScorer
from src.tablas_store import resolve_tablas
from src.table_validation import text_looks_truncated


@dataclass
class QCIssue:
    severity: str  # error | warning
    category: str  # tablas | pdf | mapa | coherencia
    message: str
    tema: str = ""

    def to_dict(self) -> dict[str, str]:
        d = asdict(self)
        if not d["tema"]:
            del d["tema"]
        return d


@dataclass
class FinalQCReport:
    passed: bool
    score: float
    tablas_score: float
    pdf_ok: bool
    issues: list[QCIssue] = field(default_factory=list)
    summary: str = ""
    recommendations: list[str] = field(default_factory=list)
    llm_review: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "tablas_score": self.tablas_score,
            "pdf_ok": self.pdf_ok,
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "llm_review": self.llm_review,
        }


class FinalQCAgent:
    """
    Revisa tablas editoriales y PDF antes de considerar el libro entregable.
    Combina reglas automáticas (rápidas) con revisión LLM opcional (coherencia).
    """

    MAX_AUTO_FIX_ROUNDS = 2

    MIN_IDEA_WORDS = 8
    MIN_EJEMPLO_WORDS = 25
    MIN_APLICACION_WORDS = 20
    MIN_PDF_BYTES = 30_000
    MIN_PNG_BYTES = 3_000
    PASS_SCORE = 0.75
    MAX_ERRORS = 0

    APLICACION_YO_MARKERS = (
        " yo ",
        "yo reviso",
        "yo priorizo",
        "me organizo",
        "aprendo que",
        "entiendo que",
        "me doy cuenta",
        "observo que",
    )
    TU_MARKERS = (
        "tú ",
        "tu ",
        "te ",
        "identifica",
        "prioriza",
        "revisa",
        "elimina",
        "organiza",
        "aplica",
        "elige",
        "detecta",
        "separa",
        "concentra",
    )

    def __init__(self, llm=None):
        self.llm = llm
        self._scorer = QualityScorer()

    def run(
        self,
        package: BookPackage,
        *,
        audiencia: str = "",
        contexto_usuario: dict | None = None,
        skip_llm: bool = False,
    ) -> FinalQCReport:
        output_dir = Path(package.output_dir)
        contexto = contexto_usuario or self._load_contexto(output_dir)
        audiencia = audiencia or contexto.get("ocupacion", "")

        tablas = resolve_tablas(output_dir, package.tablas or [])
        issues: list[QCIssue] = []

        issues.extend(self._check_tablas(tablas, package))
        issues.extend(self._check_rol_perfil(tablas, output_dir))
        issues.extend(self._check_mapa(output_dir, package))
        pdf_ok, pdf_issues = self._check_pdf(package)
        issues.extend(pdf_issues)

        tablas_score = self._score_tablas(tablas, issues)
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")

        llm_review: dict[str, Any] = {}
        if self.llm and not skip_llm and tablas:
            llm_review = self._llm_review(
                tablas,
                audiencia=audiencia,
                contexto=contexto,
                libro=package.libro_nombre,
                output_dir=output_dir,
            )
            for item in llm_review.get("issues", []):
                issues.append(
                    QCIssue(
                        severity=str(item.get("severity", "warning")),
                        category="coherencia",
                        message=str(item.get("message", "")),
                        tema=str(item.get("tema", "")),
                    )
                )

        pdf_penalty = 0.0 if pdf_ok else 0.35
        score = round(max(0.0, tablas_score - pdf_penalty - warning_count * 0.03), 2)
        passed = (
            score >= self.PASS_SCORE
            and error_count <= self.MAX_ERRORS
            and pdf_ok
        )

        recommendations = self._recommendations(issues, llm_review)
        summary = (
            f"{'✅ Aprobado' if passed else '❌ Requiere corrección'} — "
            f"score {score} | {len(tablas)} tablas | "
            f"{error_count} errores, {warning_count} avisos"
        )

        report = FinalQCReport(
            passed=passed,
            score=score,
            tablas_score=tablas_score,
            pdf_ok=pdf_ok,
            issues=issues,
            summary=summary,
            recommendations=recommendations,
            llm_review=llm_review,
        )
        self._save(report, output_dir)
        self._print(report)
        return report

    def run_with_auto_fix(
        self,
        package: BookPackage,
        *,
        audiencia: str = "",
        contexto_usuario: dict | None = None,
        skip_llm: bool = False,
        learning=None,
    ) -> FinalQCReport:
        """QC con reintentos: regenera tablas con errores automáticos y vuelve a armar PDF."""
        report = self.run(
            package,
            audiencia=audiencia,
            contexto_usuario=contexto_usuario,
            skip_llm=skip_llm,
        )
        if report.passed or not self.llm:
            return report

        for round_idx in range(1, self.MAX_AUTO_FIX_ROUNDS + 1):
            temas = self.temas_con_errores_tablas(report)
            if not temas:
                break

            print(
                f"\n🔧 QC auto-fix ({round_idx}/{self.MAX_AUTO_FIX_ROUNDS}): "
                f"regenerando {len(temas)} tabla(s)..."
            )
            package = self._regenerar_tablas(
                package,
                temas,
                contexto_usuario=contexto_usuario,
                learning=learning,
            )
            from src.agents.pdf_design_agent import PDFDesignAgent

            PDFDesignAgent(self.llm).run(package)
            report = self.run(
                package,
                audiencia=audiencia,
                contexto_usuario=contexto_usuario,
                skip_llm=skip_llm,
            )
            if report.passed:
                break

        return report

    @staticmethod
    def temas_con_errores_tablas(report: FinalQCReport) -> list[str]:
        temas: list[str] = []
        seen: set[str] = set()
        for issue in report.issues:
            if issue.category != "tablas" or issue.severity != "error":
                continue
            if issue.tema and issue.tema not in seen:
                seen.add(issue.tema)
                temas.append(issue.tema)
        return temas

    def _regenerar_tablas(
        self,
        package: BookPackage,
        temas: list[str],
        *,
        contexto_usuario: dict | None,
        learning=None,
    ) -> BookPackage:
        from src.agents.tables_agent import TablesAgent
        from src.output import write_book_summary
        from src.tablas_store import resolve_tablas

        output_dir = Path(package.output_dir)
        prompts = learning.load_all_prompts() if learning else {}
        tablas = TablesAgent(self.llm, prompts.get("tablas", [])).run(
            [r for r in package.resultados if not r.fallo],
            package.libro_nombre,
            output_dir,
            force=True,
            contexto_usuario=contexto_usuario,
            only_temas=set(temas),
        )
        merged = resolve_tablas(output_dir, tablas)
        package.tablas = merged
        if package.fecha:
            write_book_summary(
                package.libro_nombre,
                package.resultados,
                output_dir,
                package.fecha,
                package,
            )
        return package

    @staticmethod
    def load(output_dir: Path) -> FinalQCReport:
        path = final_qc_report_path(output_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        issues = [QCIssue(**i) for i in data.get("issues", [])]
        return FinalQCReport(
            passed=data.get("passed", False),
            score=data.get("score", 0.0),
            tablas_score=data.get("tablas_score", 0.0),
            pdf_ok=data.get("pdf_ok", False),
            issues=issues,
            summary=data.get("summary", ""),
            recommendations=data.get("recommendations", []),
            llm_review=data.get("llm_review", {}),
        )

    def _check_tablas(
        self, tablas: list[TopicTable], package: BookPackage
    ) -> list[QCIssue]:
        issues: list[QCIssue] = []
        temas_esperados = [r.tema for r in package.resultados if not r.fallo]

        if not tablas:
            issues.append(
                QCIssue("error", "tablas", "No hay tablas generadas o index.json vacío.")
            )
            return issues

        tablas_map = {t.tema: t for t in tablas}
        for tema in temas_esperados:
            if tema not in tablas_map:
                issues.append(
                    QCIssue("error", "tablas", f"Falta tabla para el tema «{tema}».", tema)
                )

        protagonistas: list[str] = []
        for tabla in tablas:
            issues.extend(self._check_tabla_celdas(tabla))
            issues.extend(self._check_tabla_png(tabla))
            name = collect_used_protagonists([tabla.ejemplo_practico])
            if name:
                if name[0] in protagonistas:
                    issues.append(
                        QCIssue(
                            "warning",
                            "tablas",
                            f"Protagonista repetido: {name[0]}.",
                            tabla.tema,
                        )
                    )
                protagonistas.append(name[0])

        dup_names = [
            n for n in set(protagonistas) if protagonistas.count(n) > 1
        ]
        if dup_names:
            issues.append(
                QCIssue(
                    "warning",
                    "tablas",
                    f"Nombres repetidos en ejemplos: {', '.join(dup_names)}.",
                )
            )
        return issues

    def _check_rol_perfil(
        self, tablas: list[TopicTable], output_dir: Path
    ) -> list[QCIssue]:
        from src.rol_usuario import load_rol_perfil

        profile = load_rol_perfil(output_dir)
        if not profile or not profile.prohibido:
            return []

        issues: list[QCIssue] = []
        for tabla in tablas:
            blob = " ".join(
                [
                    tabla.idea_clave or "",
                    tabla.ejemplo_practico or "",
                    tabla.aplicacion_vida_real or "",
                ]
            ).lower()
            for term in profile.prohibido:
                if term.lower() in blob:
                    issues.append(
                        QCIssue(
                            "warning",
                            "coherencia",
                            f"Lenguaje ajeno al rol («{term}»); revisar ROL_USUARIO.",
                            tabla.tema,
                        )
                    )
        return issues

    def _check_tabla_celdas(self, tabla: TopicTable) -> list[QCIssue]:
        issues: list[QCIssue] = []
        tema = tabla.tema

        for campo, texto, min_words in (
            ("idea_clave", tabla.idea_clave, self.MIN_IDEA_WORDS),
            ("ejemplo_practico", tabla.ejemplo_practico, self.MIN_EJEMPLO_WORDS),
            ("aplicacion_vida_real", tabla.aplicacion_vida_real, self.MIN_APLICACION_WORDS),
        ):
            t = (texto or "").strip()
            if not t or t in {"—", "-", "n/a"}:
                issues.append(
                    QCIssue("error", "tablas", f"Campo «{campo}» vacío.", tema)
                )
                continue
            words = len(t.split())
            if words < min_words:
                issues.append(
                    QCIssue(
                        "warning",
                        "tablas",
                        f"«{campo}» muy corto ({words} palabras, mín ~{min_words}).",
                        tema,
                    )
                )
            if text_looks_truncated(t):
                issues.append(
                    QCIssue(
                        "error",
                        "tablas",
                        f"«{campo}» parece truncado (termina sin oración completa).",
                        tema,
                    )
                )
            issues.extend(self._check_english(t, tema, campo))

        aplic = (tabla.aplicacion_vida_real or "").lower()
        padded = f" {aplic} "
        if any(m in padded for m in self.APLICACION_YO_MARKERS):
            issues.append(
                QCIssue(
                    "error",
                    "tablas",
                    "Aplicación en primera persona («yo»); debe ser imperativo en «tú».",
                    tema,
                )
            )
        elif not any(m in aplic for m in self.TU_MARKERS):
            issues.append(
                QCIssue(
                    "warning",
                    "tablas",
                    "Aplicación sin imperativos claros en segunda persona.",
                    tema,
                )
            )
        return issues

    def _check_tabla_png(self, tabla: TopicTable) -> list[QCIssue]:
        issues: list[QCIssue] = []
        path = tabla.image_path
        if not path or not Path(path).exists():
            issues.append(
                QCIssue("error", "tablas", "PNG de tarjeta no encontrado.", tabla.tema)
            )
            return issues
        if Path(path).stat().st_size < self.MIN_PNG_BYTES:
            issues.append(
                QCIssue(
                    "warning",
                    "tablas",
                    "PNG de tarjeta sospechoso de vacío o corrupto.",
                    tabla.tema,
                )
            )
        return issues

    def _check_english(self, texto: str, tema: str, campo: str) -> list[QCIssue]:
        words = texto.split()
        if not words:
            return []
        english_count = sum(
            1 for w in words if w.lower().strip(".,;:") in self._scorer.ENGLISH_MARKERS
        )
        ratio = english_count / len(words)
        if ratio > self._scorer.MAX_ENGLISH_RATIO:
            return [
                QCIssue(
                    "warning",
                    "tablas",
                    f"«{campo}» con posible mezcla de inglés ({ratio:.0%}).",
                    tema,
                )
            ]
        anglicisms = ("engagement", "feedback", "deadline", "workflow", "mindset")
        found = [a for a in anglicisms if a in texto.lower()]
        if found:
            return [
                QCIssue(
                    "warning",
                    "tablas",
                    f"«{campo}» contiene anglicismos: {', '.join(found)}.",
                    tema,
                )
            ]
        return []

    def _check_mapa(
        self, output_dir: Path, package: BookPackage
    ) -> list[QCIssue]:
        mapa = package.mapa_path or resolve_mapa_png(output_dir)
        if mapa and Path(mapa).exists():
            return []
        return [
            QCIssue(
                "warning",
                "mapa",
                "Mapa conceptual no encontrado (el PDF puede generarse sin mapa).",
            )
        ]

    def _check_pdf(self, package: BookPackage) -> tuple[bool, list[QCIssue]]:
        issues: list[QCIssue] = []
        pdf = package.pdf_path
        if not pdf:
            pdf = self._find_pdf(package.output_dir, package.libro_nombre)
        if not pdf or not Path(pdf).exists():
            issues.append(QCIssue("error", "pdf", "PDF final no encontrado."))
            return False, issues
        size = Path(pdf).stat().st_size
        if size < self.MIN_PDF_BYTES:
            issues.append(
                QCIssue(
                    "error",
                    "pdf",
                    f"PDF demasiado pequeño ({size // 1024} KB); posible fallo de render.",
                )
            )
            return False, issues
        return True, issues

    def _llm_review(
        self,
        tablas: list[TopicTable],
        *,
        audiencia: str,
        contexto: dict,
        libro: str,
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        from src.rol_usuario import build_rol_block, load_rol_perfil

        profile = load_rol_perfil(output_dir) if output_dir else None
        rol_block = build_rol_block(profile, agent="qc") if profile else ""
        muestra = []
        for t in tablas[:12]:
            muestra.append(
                {
                    "tema": t.tema,
                    "idea_clave": t.idea_clave,
                    "ejemplo_practico": t.ejemplo_practico,
                    "aplicacion_vida_real": t.aplicacion_vida_real,
                }
            )
        prompt = f"""Eres el revisor de calidad FINAL de un resumen PDF editorial.

Libro: «{libro}»
Audiencia objetivo: {audiencia or "no indicada"}
Contexto lector: {json.dumps(contexto, ensure_ascii=False)}

{rol_block}

Tablas (muestra):
{json.dumps(muestra, ensure_ascii=False, indent=2)}

Evalúa SOLO:
1. ¿Los ejemplos y aplicaciones usan léxico, KPIs y metodología del ROL_USUARIO?
2. ¿Hay lenguaje genérico o de otros dominios (negocio, clínica, aula…) fuera del rol?
3. ¿Hay repeticiones de escenarios entre temas?
4. ¿La aplicación en vida real está en imperativo «tú», no en «yo»?
5. ¿Hay anglicismos o tono de autoayuda vacía?

Responde SOLO JSON:
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "issues": [
    {{"severity": "error|warning", "tema": "...", "message": "..."}}
  ],
  "recommendations": ["..."]
}}"""
        try:
            raw = self.llm.call(prompt)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                return {}
            return json.loads(match.group())
        except Exception as exc:
            return {"error": str(exc)}

    def _score_tablas(self, tablas: list[TopicTable], issues: list[QCIssue]) -> float:
        if not tablas:
            return 0.0
        base = 1.0
        for issue in issues:
            if issue.category != "tablas":
                continue
            base -= 0.12 if issue.severity == "error" else 0.05
        return round(max(0.0, min(1.0, base)), 2)

    def _recommendations(
        self, issues: list[QCIssue], llm_review: dict
    ) -> list[str]:
        recs: list[str] = []
        cats = {i.category for i in issues if i.severity == "error"}
        if "tablas" in cats:
            recs.append("Regenera tablas: python main.py LIBRO --solo-tablas --slug SLUG")
        if "pdf" in cats:
            recs.append("Regenera PDF: python main.py LIBRO --solo-pdf --slug SLUG")
        if any(i.category == "coherencia" for i in issues):
            recs.append(
                "Revisa contexto_usuario.json y meta/instrucciones_tablas.json, "
                "luego vuelve a generar tablas."
            )
        for r in llm_review.get("recommendations", []):
            if r and r not in recs:
                recs.append(str(r))
        return recs[:6]

    def _save(self, report: FinalQCReport, output_dir: Path) -> Path:
        path = final_qc_report_path(output_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def _print(self, report: FinalQCReport) -> None:
        print(f"\n🔍 QC final: {report.summary}")
        errores = [i for i in report.issues if i.severity == "error"]
        avisos = [i for i in report.issues if i.severity == "warning"]
        for issue in errores[:8]:
            tema = f" [{issue.tema}]" if issue.tema else ""
            print(f"   ❌ {issue.category}{tema}: {issue.message}")
        for issue in avisos[:5]:
            tema = f" [{issue.tema}]" if issue.tema else ""
            print(f"   ⚠️  {issue.category}{tema}: {issue.message}")
        if report.recommendations:
            print("   💡 Recomendaciones:")
            for r in report.recommendations[:4]:
                print(f"      · {r}")

    @staticmethod
    def _load_contexto(output_dir: Path) -> dict:
        path = Path(output_dir) / "contexto_usuario.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def _find_pdf(output_dir: Path, libro_nombre: str) -> Path | None:
        output_dir = Path(output_dir)
        for pdf in sorted(output_dir.glob("*.pdf")):
            if pdf.stat().st_size >= FinalQCAgent.MIN_PDF_BYTES:
                return pdf
        safe = re.sub(r"[^a-zA-Z0-9 -_,]", "_", libro_nombre).strip()[:80]
        candidate = output_dir / f"{safe}.pdf"
        return candidate if candidate.exists() else None


def run_qc_for_slug(slug: str, *, skip_llm: bool = False) -> int:
    """Ejecuta QC final sobre resumenes/{slug}. Retorna 0 si aprueba, 2 si falla."""
    from src.config import ANTHROPIC_API_KEY, RESUMENES_DIR
    from src.md_loader import find_summary_md, parse_enriched_markdown
    from src.output_paths import resolve_mapa_png
    from src.tablas_store import resolve_tablas

    output_dir = RESUMENES_DIR / slug
    if not output_dir.is_dir():
        print(f"❌ No existe resumenes/{slug}/")
        return 1

    md_path = find_summary_md(output_dir)
    libro, resultados, tablas_md, _ = parse_enriched_markdown(md_path)
    tablas = resolve_tablas(output_dir, tablas_md)
    pdf = next(
        (p for p in sorted(output_dir.glob("*.pdf")) if p.stat().st_size > 30_000),
        None,
    )

    package = BookPackage(
        libro_nombre=libro,
        libro_slug=slug,
        output_dir=output_dir,
        resultados=resultados,
        tablas=tablas,
        mapa_path=resolve_mapa_png(output_dir),
        pdf_path=pdf,
    )

    llm = None
    if not skip_llm and ANTHROPIC_API_KEY:
        from src.llm import LLMClient
        llm = LLMClient(ANTHROPIC_API_KEY)

    audiencia = ""
    contexto: dict = {}
    try:
        from src.agents.planner_agent import PlannerAgent
        plan = PlannerAgent.load(output_dir)
        audiencia = plan.audiencia
        contexto = plan.contexto_usuario
    except FileNotFoundError:
        contexto = FinalQCAgent._load_contexto(output_dir)

    report = FinalQCAgent(llm).run_with_auto_fix(
        package,
        audiencia=audiencia,
        contexto_usuario=contexto,
        skip_llm=llm is None,
    )
    return 0 if report.passed else 2

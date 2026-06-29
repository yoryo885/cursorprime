from pathlib import Path
from typing import Optional

from src.agents.book_package import BookPackage
from src.config import VOZ_NOMBRE
from src.html_renderer import html_string_to_pdf, render_book_html, write_html
from src.output_paths import ensure_book_dirs, html_dir, intro_path, resolve_intro_path


class PDFDesignAgent:
    """Ensambla portada, temas y tablas en PDF con HTML + Playwright."""

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, package: BookPackage) -> Path:
        print("   📄 Agente PDF: ensamblando PDF con Playwright...")
        ensure_book_dirs(package.output_dir)
        book_html_dir = html_dir(package.output_dir)
        book_html_dir.mkdir(parents=True, exist_ok=True)

        llm = self._resolve_llm()
        temas = [r.tema for r in package.resultados if not r.fallo]
        intro_file = resolve_intro_path(package.output_dir)
        force_intro = False
        if llm and intro_file.exists():
            force_intro = _is_placeholder_intro(
                intro_file.read_text(encoding="utf-8")
            )
        package.introduccion = clean_intro_text(
            load_or_create_intro(
                package.output_dir,
                package.libro_nombre,
                llm=llm,
                temas=temas,
                force_regenerate=force_intro,
            )
        )

        safe = _safe_filename(package.libro_nombre)
        html_path = book_html_dir / f"{safe}.html"
        pdf_path = package.output_dir / f"{safe}.pdf"

        book_html = render_book_html(
            package,
            voz_nombre=VOZ_NOMBRE,
            html_dir=book_html_dir,
        )
        write_html(html_path, book_html)

        print("      → Convirtiendo HTML a PDF con Chromium...")
        html_string_to_pdf(book_html, html_path, pdf_path)

        package.pdf_path = pdf_path
        num_temas = len([r for r in package.resultados if not r.fallo])
        tablas_map = {t.tema: t for t in package.tablas}
        tablas_n = sum(
            1 for r in package.resultados
            if not r.fallo
            and (t := tablas_map.get(r.tema))
            and t.idea_clave
        )
        from src.output_paths import resolve_mapa_estructura

        tiene_mapa = package.mapa_path or resolve_mapa_estructura(package.output_dir)
        paginas = 1 + (1 if tiene_mapa else 0) + num_temas + tablas_n
        print(f"      ✓ PDF final (~{paginas} páginas): {pdf_path.name}")
        return pdf_path

    def _resolve_llm(self):
        if self.llm:
            return self.llm
        try:
            from src.config import ANTHROPIC_API_KEY
            from src.llm import LLMClient
            if ANTHROPIC_API_KEY:
                return LLMClient(ANTHROPIC_API_KEY)
        except ImportError:
            pass
        return None


def clean_intro_text(text: str) -> str:
    """Quita la línea de edición manual — no debe aparecer en el PDF."""
    lines = [
        line
        for line in (text or "").splitlines()
        if "Puedes editar este texto en introduccion.txt" not in line
    ]
    return "\n".join(lines).strip()


def load_or_create_intro(
    output_dir: Path,
    libro_nombre: str,
    llm=None,
    temas: Optional[list[str]] = None,
    *,
    force_regenerate: bool = False,
) -> str:
    dest = intro_path(output_dir)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temas = temas or []
    if not force_regenerate:
        for candidate in (dest, Path(output_dir) / "introduccion.txt"):
            if candidate.exists():
                return clean_intro_text(candidate.read_text(encoding="utf-8"))
    if llm:
        from src.agents.intro_agent import IntroAgent
        intro = IntroAgent(llm).run(libro_nombre, temas)
    else:
        intro = _default_intro(libro_nombre)
    dest.write_text(intro, encoding="utf-8")
    return clean_intro_text(intro)


def _is_placeholder_intro(text: str) -> bool:
    return "Puedes editar este texto en introduccion.txt" in (text or "")


def _default_intro(libro_nombre: str) -> str:
    return (
        f"Esto no es un resumen de «{libro_nombre}».\n\n"
        f"Es lo que me quedó después de leerlo — "
        f"las ideas que me hicieron detenerme. Pensar. "
        f"Conectar algo del libro con algo mío.\n\n"
        f"Escrito con mis palabras. Desde mi cabeza.\n"
        f"Si algo resuena, ve al libro original.\n"
        f"Si algo incomoda, mejor todavía."
    )


def _safe_filename(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in " -_," else "_" for c in name)
    return safe.strip()[:80] or "resumen"

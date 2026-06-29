from datetime import datetime
from pathlib import Path
from typing import Optional

from src.agents.book_package import BookPackage, TopicTable
from src.config import VOZ_NOMBRE, TEMA_RESUMEN_ETIQUETA
from src.models import TopicResult
from src.text_sanitize import clean_resumen_markdown


def write_book_summary(
    libro_nombre: str,
    resultados: list[TopicResult],
    output_dir: Path,
    fecha: Optional[datetime] = None,
    package: Optional[BookPackage] = None,
) -> Path:
    """Escribe markdown enriquecido en la subcarpeta del libro."""
    fecha = fecha or datetime.now()
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_filename(libro_nombre)
    md_path = output_dir / f"{safe_name}.md"
    md_path.write_text(
        _build_markdown(libro_nombre, resultados, fecha, package),
        encoding="utf-8",
    )
    return md_path


def _build_markdown(
    libro_nombre: str,
    resultados: list[TopicResult],
    fecha: datetime,
    package: Optional[BookPackage] = None,
) -> str:
    tablas_map: dict[str, TopicTable] = {}
    if package and package.tablas:
        tablas_map = {t.tema: t for t in package.tablas}

    lineas = [
        f"# Resumen: {libro_nombre}",
        "",
        f"**Fecha de procesamiento:** {fecha.strftime('%d/%m/%Y %H:%M')}",
        f"**Temas procesados:** {len(resultados)}",
        "",
    ]

    if package and package.mapa_path:
        try:
            rel_mapa = package.mapa_path.relative_to(package.output_dir).as_posix()
        except ValueError:
            rel_mapa = package.mapa_path.name
        lineas.extend([
            f"**Mapa conceptual:** `{rel_mapa}`",
            "",
        ])

    lineas.extend(["---", ""])

    for resultado in resultados:
        lineas.extend([f"## {resultado.tema}", ""])
        if resultado.fallo:
            lineas.append("> ⚠️ *Este tema falló durante el procesamiento.*")
            lineas.append("")

        texto = clean_resumen_markdown(resultado.resumen_voz or resultado.resumen)
        if texto:
            lineas.extend([
                f"### {TEMA_RESUMEN_ETIQUETA}",
                "",
                texto,
                "",
            ])

        tabla = tablas_map.get(resultado.tema)
        if tabla:
            if tabla.image_path and tabla.image_path.exists():
                rel = f"tablas/{tabla.image_path.name}"
                lineas.extend(["### Tabla", ""])
                if tabla.image_path.suffix.lower() == ".html":
                    lineas.append(f"[Tabla {resultado.tema}]({rel})")
                else:
                    lineas.append(f"![Tabla {resultado.tema}]({rel})")
                lineas.append("")
            elif tabla.idea_clave:
                lineas.extend([
                    "### Tabla",
                    "",
                    "| Idea clave | Ejemplo práctico | Aplicación en la vida real |",
                    "|---|---|---|",
                    f"| {tabla.idea_clave} | {tabla.ejemplo_practico} | {tabla.aplicacion_vida_real} |",
                    "",
                ])

        if package and resultado.tema in package.imagenes:
            lineas.append(
                f"![{resultado.tema}](imagenes/{package.imagenes[resultado.tema].name})"
            )
            lineas.append("")

        if resultado.fragmentos:
            lineas.append("### Ideas del PDF")
            lineas.append("")
            for i, fragmento in enumerate(resultado.fragmentos, 1):
                truncado = fragmento[:500] + ("..." if len(fragmento) > 500 else "")
                lineas.extend([f"**{i}.**", "", f"> {truncado}", ""])

        lineas.extend(["---", ""])

    return "\n".join(lineas)


def _safe_filename(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in " -_," else "_" for c in name)
    return safe.strip()[:80] or "resumen"

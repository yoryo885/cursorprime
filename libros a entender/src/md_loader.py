import re
from datetime import datetime
from pathlib import Path

from src.agents.book_package import TopicTable
from src.models import TopicResult
from src.text_sanitize import clean_resumen_markdown


def find_summary_md(output_dir: Path) -> Path:
    """Encuentra el .md de resumen en la carpeta del libro."""
    output_dir = Path(output_dir)
    candidates = sorted(output_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No hay resumen .md en {output_dir}")
    return candidates[0]


def parse_enriched_markdown(md_path: Path) -> tuple[str, list[TopicResult], list[TopicTable], datetime]:
    """Parsea el markdown enriquecido generado por el sistema."""
    text = md_path.read_text(encoding="utf-8")
    output_dir = md_path.parent

    title_m = re.search(r"^#\s*Resumen:\s*(.+)$", text, re.M)
    libro = title_m.group(1).strip() if title_m else md_path.stem

    fecha_m = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})", text)
    fecha = datetime.now()
    if fecha_m:
        try:
            fecha = datetime.strptime(fecha_m.group(1), "%d/%m/%Y %H:%M")
        except ValueError:
            pass

    resultados: list[TopicResult] = []
    tablas: list[TopicTable] = []

    blocks: list[tuple[str, str]] = []
    for block in re.split(r"\n##\s+", text)[1:]:
        lines = block.strip().split("\n")
        tema = lines[0].strip()
        body = "\n".join(lines[1:])
        if tema == "Resumen" and blocks:
            prev_tema, prev_body = blocks[-1]
            if prev_body and body:
                merged_body = f"{prev_body.rstrip()}\n\n{body}"
            elif body:
                merged_body = body
            else:
                merged_body = prev_body
            blocks[-1] = (prev_tema, merged_body)
            continue
        blocks.append((tema, body))

    for tema, body in blocks:
        voz_m = re.search(
            r"### (?:Lo que aprendí \(Yordy\)|Para ti)\s*\n\n?(.*?)(?=\n###|\n---|\Z)", body, re.S
        )
        res_m = re.search(
            r"### Resumen\s*\n\n(.*?)(?=\n###|\n---|\Z)", body, re.S
        )
        # Formato antiguo sin subsección Resumen
        if not res_m and not voz_m:
            old_body = re.split(r"### Fragmentos|\n---", body)[0].strip()
            if old_body and not old_body.startswith(">"):
                res_m = type("M", (), {"group": lambda s, i=1: old_body})()

        tab_m = re.search(
            r"\| Idea clave.*?\n\|---.*?\n\| (.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|",
            body,
            re.S,
        )
        tab_img_m = re.search(r"!\[Tabla.*?\]\((tablas/[^)]+)\)", body)
        frags = re.findall(r"> (.+)", body)

        resumen = clean_resumen_markdown(res_m.group(1).strip() if res_m else "")
        resumen_voz = clean_resumen_markdown(voz_m.group(1).strip() if voz_m else "")

        r = TopicResult(
            tema=tema,
            resumen=resumen,
            resumen_voz=resumen_voz,
            fragmentos=frags,
        )
        resultados.append(r)

        if tab_m:
            tab_img_path = None
            if tab_img_m:
                tab_img_path = output_dir / tab_img_m.group(1)
            tablas.append(
                TopicTable(
                    tema=tema,
                    idea_clave=tab_m.group(1).strip(),
                    ejemplo_practico=tab_m.group(2).strip(),
                    aplicacion_vida_real=tab_m.group(3).strip(),
                    image_path=tab_img_path if tab_img_path and tab_img_path.exists() else None,
                )
            )
        elif tab_img_m:
            tab_img_path = output_dir / tab_img_m.group(1)
            tablas.append(
                TopicTable(
                    tema=tema,
                    idea_clave="",
                    ejemplo_practico="",
                    aplicacion_vida_real="",
                    image_path=tab_img_path if tab_img_path.exists() else None,
                )
            )

    return libro, resultados, tablas, fecha


def list_temas_from_results(resultados: list[TopicResult]) -> list[str]:
    return [r.tema for r in resultados]

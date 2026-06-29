"""Persistencia y carga de datos de tablas para el PDF."""
import json
import re
from pathlib import Path

from src.agents._paths import tema_slug
from src.agents.book_package import TopicTable

INDEX_FILENAME = "index.json"


def save_tablas_index(tablas_dir: Path, tablas: list[TopicTable]) -> Path:
    tablas_dir = Path(tablas_dir)
    tablas_dir.mkdir(parents=True, exist_ok=True)
    data = []
    for t in tablas:
        data.append({
            "tema": t.tema,
            "idea_clave": t.idea_clave,
            "ejemplo_practico": t.ejemplo_practico,
            "aplicacion_vida_real": t.aplicacion_vida_real,
            "image_path": str(t.image_path) if t.image_path else None,
        })
    path = tablas_dir / INDEX_FILENAME
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_tablas_index(tablas_dir: Path) -> list[TopicTable]:
    path = Path(tablas_dir) / INDEX_FILENAME
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    tablas = []
    for item in raw:
        img = item.get("image_path")
        tablas.append(
            TopicTable(
                tema=item.get("tema", ""),
                idea_clave=item.get("idea_clave", ""),
                ejemplo_practico=item.get("ejemplo_practico", ""),
                aplicacion_vida_real=item.get("aplicacion_vida_real", ""),
                image_path=Path(img) if img else None,
            )
        )
    return tablas


def load_tablas_from_html_dir(tablas_dir: Path) -> list[TopicTable]:
    """Recupera datos parseando los HTML generados por el agente de tablas."""
    tablas_dir = Path(tablas_dir)
    if not tablas_dir.is_dir():
        return []

    tablas: list[TopicTable] = []
    for html_path in sorted(tablas_dir.glob("*.html")):
        if html_path.name.startswith("_"):
            continue
        text = html_path.read_text(encoding="utf-8")
        tema_m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        if not tema_m:
            continue
        tema = re.sub(r"<[^>]+>", "", tema_m.group(1)).strip()
        celdas = re.findall(
            r'<div class="tbl-editorial-body">\s*<strong>.*?</strong>\s*<p>(.*?)</p>',
            text,
            re.S,
        )
        if len(celdas) < 3:
            continue
        slug = html_path.stem
        png = tablas_dir / f"{slug}.png"
        tablas.append(
            TopicTable(
                tema=tema,
                idea_clave=_unesc(celdas[0]),
                ejemplo_practico=_unesc(celdas[1]),
                aplicacion_vida_real=_unesc(celdas[2]),
                image_path=png if png.exists() else html_path,
            )
        )
    return tablas


def merge_tablas(*sources: list[TopicTable]) -> list[TopicTable]:
    """Fusiona tablas; las fuentes posteriores tienen mayor prioridad."""
    merged: dict[str, TopicTable] = {}
    for items in sources:
        for t in items:
            if not t.tema:
                continue
            prev = merged.get(t.tema)
            if prev is None or _tabla_mas_completa(t, prev):
                merged[t.tema] = t
    return list(merged.values())


def _tabla_mas_completa(nueva: TopicTable, prev: TopicTable) -> bool:
    """True si la entrada nueva aporta más contenido útil que la anterior."""
    score_n = _tabla_score(nueva)
    score_p = _tabla_score(prev)
    if score_n != score_p:
        return score_n > score_p
    return bool(nueva.aplicacion_vida_real and not prev.aplicacion_vida_real)


def _tabla_score(t: TopicTable) -> int:
    score = 0
    if (t.idea_clave or "").strip():
        score += 2
    if (t.ejemplo_practico or "").strip():
        score += 0
    if (t.aplicacion_vida_real or "").strip():
        score += 4
    if t.image_path and Path(t.image_path).suffix.lower() == ".png":
        if Path(t.image_path).exists():
            score += 1
    return score


def resolve_tablas(output_dir: Path, tablas_md: list[TopicTable]) -> list[TopicTable]:
    from src.output_paths import tablas_dir as book_tablas_dir

    tablas_dir = book_tablas_dir(output_dir)
    # index.json e HTML de tablas son la fuente de verdad; el .md puede quedar obsoleto
    return merge_tablas(
        tablas_md,
        load_tablas_from_html_dir(tablas_dir),
        load_tablas_index(tablas_dir),
    )


def _unesc(text: str) -> str:
    return (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .strip()
    )

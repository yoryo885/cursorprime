import json
import re
from pathlib import Path
from typing import Optional

from src.html_renderer import html_to_png, render_map_page_html, write_html
from src.output_paths import (
    ensure_book_dirs,
    mapa_dir,
    mapa_estructura_path,
    mapa_html_path,
    mapa_png_path,
    resolve_mapa_png,
)

TEMAS_EXCLUIDOS = {"resumen", "summary", "introducción", "introduction", "índice"}


def _filtrar_temas_mapa(temas: list[str]) -> list[str]:
    return [t for t in temas if t.lower().strip() not in TEMAS_EXCLUIDOS]


class MapAgent:
    """Claude genera la estructura; HTML/CSS + Playwright renderiza el mapa."""

    def __init__(self, llm, prompt_extra: Optional[list[str]] = None):
        self.llm = llm
        self.prompt_extra = prompt_extra or []

    def run(
        self,
        temas: list[str],
        libro_nombre: str,
        output_dir: Path,
        *,
        force: bool = False,
    ) -> Optional[Path]:
        print("   🗺️  Agente Mapa: Claude + HTML/CSS + Playwright...")
        ensure_book_dirs(output_dir)
        m_dir = mapa_dir(output_dir)
        png_dest = mapa_png_path(output_dir)
        html_dest = mapa_html_path(output_dir)
        estructura_dest = mapa_estructura_path(output_dir)

        if not force:
            cached = resolve_mapa_png(output_dir)
            if cached:
                print(f"      ✓ Mapa en caché: {cached.relative_to(output_dir)}")
                return cached

        if force:
            for path in (png_dest, html_dest, estructura_dest):
                if path.exists():
                    path.unlink()

        try:
            temas_filtrados = _filtrar_temas_mapa(temas)
            categorias, conexiones = self._obtener_estructura(
                temas_filtrados, libro_nombre
            )
            estructura_dest.write_text(
                json.dumps(
                    {
                        "libro_nombre": libro_nombre,
                        "temas": temas_filtrados,
                        "categorias": categorias,
                        "conexiones": [
                            {"desde": d, "hasta": h, "relacion": r}
                            for d, h, r in conexiones
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            content = render_map_page_html(
                temas_filtrados, categorias, conexiones, libro_nombre
            )
            write_html(html_dest, content)
            print(f"      → Playwright render: {png_dest.name}")
            html_to_png(html_dest, png_dest)
            print(f"      ✓ Mapa guardado: {m_dir.name}/{png_dest.name}")
            return png_dest
        except Exception as err:
            print(f"      ⚠️  Mapa falló: {err}")
            return None

    def _obtener_estructura(
        self, temas: list[str], libro_nombre: str
    ) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
        temas_list = "\n".join(f"- {t}" for t in temas)
        extra = "\n".join(f"- {i}" for i in self.prompt_extra)
        extra_block = f"\nInstrucciones extra:\n{extra}\n" if extra else ""

        prompt = f"""Eres un agente de mapas conceptuales para libros.

Libro: {libro_nombre}
Temas:
{temas_list}
{extra_block}
Antes de dibujar el mapa, analiza los temas en dos pasos:

PASO 1 — Categorías:
Agrupa cada tema en una categoría conceptual (2-4 palabras).
Temas de la misma categoría comparten color en el mapa.
Ejemplos de categorías: "procesos mentales", "sesgos y errores", "decisiones y economía".

PASO 2 — Conexiones con explicación real:
Identifica 8-12 conexiones entre temas.
Cada conexión debe explicar POR QUÉ se relacionan dos temas (causa, consecuencia, dependencia, contraste, etc.).
La etiqueta "relacion" debe ser una frase corta pero significativa (3-8 palabras), NO genérica.
Prohibido usar etiquetas vacías como "relacionado", "se conecta con" o "vinculado".

Responde SOLO con JSON:
{{
  "categorias": {{"nombre exacto del tema": "nombre categoría", ...}},
  "conexiones": [
    {{"desde": "tema A", "hasta": "tema B", "relacion": "explica la conexión real entre ambos"}}
  ]
}}"""

        raw = self.llm.call(prompt)
        return self._parse_estructura(raw, temas)

    def _parse_estructura(
        self, text: str, temas: list[str]
    ) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
        categorias: dict[str, str] = {}
        conexiones: list[tuple[str, str, str]] = []

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                raw_cat = data.get("categorias", {})
                if isinstance(raw_cat, dict):
                    for tema in temas:
                        cat = raw_cat.get(tema) or raw_cat.get(tema.strip())
                        categorias[tema] = str(cat) if cat else "General"

                for item in data.get("conexiones", []):
                    desde = str(item.get("desde", ""))
                    hasta = str(item.get("hasta", ""))
                    rel = str(item.get("relacion", "")).strip()
                    if desde in temas and hasta in temas and self._etiqueta_valida(rel):
                        conexiones.append((desde, hasta, rel))
            except json.JSONDecodeError:
                pass

        for tema in temas:
            categorias.setdefault(tema, "General")

        if not conexiones and len(temas) > 1:
            conexiones = self._conexiones_fallback(temas, categorias)

        return categorias, conexiones

    def _etiqueta_valida(self, rel: str) -> bool:
        if not rel or len(rel) < 4:
            return False
        genericas = {"relacionado", "se conecta con", "vinculado", "conecta con", "asociado"}
        return rel.lower().strip() not in genericas

    def _conexiones_fallback(
        self, temas: list[str], categorias: dict[str, str]
    ) -> list[tuple[str, str, str]]:
        conexiones = []
        por_cat: dict[str, list[str]] = {}
        for t in temas:
            por_cat.setdefault(categorias.get(t, "General"), []).append(t)

        for miembros in por_cat.values():
            if len(miembros) > 1:
                for i in range(len(miembros) - 1):
                    conexiones.append((
                        miembros[i],
                        miembros[i + 1],
                        "comparte la misma categoría conceptual",
                    ))

        if not conexiones:
            hub = temas[0]
            for t in temas[1:3]:
                conexiones.append((hub, t, "articula ideas del mismo marco teórico"))

        return conexiones

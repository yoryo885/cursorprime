"""Marca de serie «Aplicar en tu rol» — títulos, portada y metadata KDP."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.config import SERIE_CONFIG_PATH

KDP_LISTING_FILENAME = "kdp_listing.json"


def _load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else default
    except (OSError, json.JSONDecodeError):
        return default


def load_serie_config() -> dict[str, Any]:
    default = {
        "nombre_serie": "Aplicar en tu rol",
        "marca_editorial": "Libros a Entender",
        "voz": "Yordy",
        "mercados_amazon": ["MX", "ES"],
        "precio_sugerido_usd": 3.99,
        "hooks_por_familia_rol": {"generico": "aplicar las ideas en tu trabajo real"},
        "disclaimer_kdp": "",
    }
    return {**default, **_load_json(SERIE_CONFIG_PATH, default)}


def concepto_corto(libro_nombre: str) -> str:
    titulo = libro_nombre.split(" - ", 1)[0].strip()
    t = titulo.lower()
    if "pareto" in t:
        return "Pareto"
    m = re.search(r"principio de (\w+)", t)
    if m:
        return m.group(1).capitalize()
    words = [w for w in re.split(r"\W+", titulo) if len(w) > 3]
    return words[0] if words else "el libro"


def libro_titulo_corto(libro_nombre: str) -> str:
    return libro_nombre.split(" - ", 1)[0].strip()


def libro_autor(libro_nombre: str) -> str:
    parts = libro_nombre.split(" - ", 1)
    return parts[1].strip() if len(parts) > 1 else ""


def rol_plural(audiencia: str) -> str:
    """«psicopedagoga en escuela» → «psicopedagogas»."""
    texto = (audiencia or "").strip()
    if " en " in texto:
        texto = texto.split(" en ", 1)[0].strip()
    if not texto:
        return "profesionales"
    base = texto.lower()
    if base.endswith("a"):
        return base[:-1] + "as"
    if base.endswith("o"):
        return base[:-1] + "os"
    if base.endswith("e"):
        return base + "s"
    return base + "s"


def hook_para_rol(
    familia_rol: str = "",
    *,
    reto: str = "",
    config: dict | None = None,
) -> str:
    cfg = config or load_serie_config()
    hooks = cfg.get("hooks_por_familia_rol") or {}
    if familia_rol and familia_rol in hooks:
        return str(hooks[familia_rol])
    if reto:
        texto = reto.strip().rstrip(".")
        if len(texto) <= 60:
            return texto[0].lower() + texto[1:] if texto else str(hooks.get("generico", ""))
    return str(hooks.get("generico", "aplicar las ideas en tu trabajo real"))


def titulo_comercial(
    *,
    libro_nombre: str,
    audiencia: str,
    familia_rol: str = "",
    reto: str = "",
    hook: str = "",
) -> str:
    cfg = load_serie_config()
    concepto = concepto_corto(libro_nombre)
    plural = rol_plural(audiencia)
    hook_final = hook or hook_para_rol(familia_rol, reto=reto, config=cfg)
    patron = str(cfg.get("patron_titulo_comercial") or "{concepto} para {rol_plural}: {hook}")
    return patron.format(
        concepto=concepto,
        rol_plural=plural,
        hook=hook_final,
        nombre_serie=cfg.get("nombre_serie", "Aplicar en tu rol"),
    )


def subtitulo_portada(libro_nombre: str) -> str:
    cfg = load_serie_config()
    patron = str(
        cfg.get("patron_subtitulo_portada")
        or "Serie {nombre_serie} · {libro_titulo}"
    )
    return patron.format(
        nombre_serie=cfg.get("nombre_serie", "Aplicar en tu rol"),
        libro_titulo=libro_titulo_corto(libro_nombre),
    )


def label_portada() -> str:
    return str(load_serie_config().get("nombre_serie") or "Aplicar en tu rol")


def kdp_listing_path(output_dir: Path) -> Path:
    return Path(output_dir) / "meta" / KDP_LISTING_FILENAME


def build_kdp_listing(
    *,
    libro_nombre: str,
    audiencia: str,
    familia_rol: str = "",
    reto: str = "",
    hook: str = "",
    num_temas: int = 0,
    num_semanas: int = 10,
) -> dict[str, Any]:
    cfg = load_serie_config()
    concepto = concepto_corto(libro_nombre)
    titulo = titulo_comercial(
        libro_nombre=libro_nombre,
        audiencia=audiencia,
        familia_rol=familia_rol,
        reto=reto,
        hook=hook,
    )
    autor_libro = libro_autor(libro_nombre)
    libro_titulo = libro_titulo_corto(libro_nombre)
    serie = str(cfg.get("nombre_serie") or "Aplicar en tu rol")
    marca = str(cfg.get("marca_editorial") or "Libros a Entender")
    disclaimer = str(cfg.get("disclaimer_kdp") or "").strip()
    rol = rol_plural(audiencia)

    subtitulo_kdp = f"Guía práctica para {rol} · Serie {serie}"

    descripcion_parrafos = [
        f"¿Trabajas como {audiencia or rol} y sientes que el tiempo nunca alcanza?",
        f"«{titulo}» es una guía de la serie <b>{serie}</b> ({marca}): "
        f"aprende las ideas clave de <i>{libro_titulo}</i>"
        + (f" ({autor_libro})" if autor_libro else "")
        + " y aplícalas directamente en tu contexto profesional.",
        "<b>Qué incluye esta guía:</b>",
        "• Resúmenes claros por tema, adaptados a tu rol",
        "• Mapa conceptual para ver cómo encajan las ideas",
        "• Tarjetas de aplicación: idea clave, ejemplo y acción concreta",
        f"• Plan de acción de {num_semanas} semanas listo para usar",
        "<b>Para quién es:</b> "
        + (audiencia or f"profesionales en el rol de {rol}"),
        "<b>Importante:</b> " + disclaimer,
    ]
    descripcion_html = "<br><br>".join(descripcion_parrafos)

    keywords = [
        f"{concepto.lower()} {rol}",
        f"guía {concepto.lower()} {audiencia.split(' en ')[0].strip() if audiencia else rol}",
        f"aplicar {concepto.lower()} trabajo",
        f"resumen {libro_titulo.lower()} profesional",
        serie.lower(),
        f"{concepto.lower()} educación" if "escuela" in (audiencia or "") else f"{concepto.lower()} productividad",
        f"plan acción {concepto.lower()}",
    ]
    keywords = [k.strip() for k in keywords if k.strip()][:7]

    return {
        "serie": serie,
        "marca": marca,
        "titulo_kdp": titulo[:200],
        "subtitulo_kdp": subtitulo_kdp[:200],
        "descripcion_html": descripcion_html,
        "keywords": keywords,
        "categorias_bisac_sugeridas": [
            "EDU000000 - EDUCATION / General",
            "SEL000000 - SELF-HELP / General",
        ],
        "mercados": cfg.get("mercados_amazon", ["MX", "ES"]),
        "precio_usd": cfg.get("precio_sugerido_usd", 3.99),
        "libro_fuente": libro_nombre,
        "audiencia": audiencia,
        "num_temas": num_temas,
        "disclaimer": disclaimer,
        "titulo_portada_pdf": titulo,
        "subtitulo_portada_pdf": subtitulo_portada(libro_nombre),
        "label_portada": label_portada(),
    }


def save_kdp_listing(output_dir: Path, listing: dict[str, Any]) -> Path:
    path = kdp_listing_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(listing, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def ensure_kdp_listing(
    output_dir: Path,
    *,
    libro_nombre: str,
    audiencia: str = "",
    familia_rol: str = "",
    reto: str = "",
    num_temas: int = 0,
    num_semanas: int = 10,
    force: bool = False,
) -> dict[str, Any]:
    path = kdp_listing_path(output_dir)
    if path.exists() and not force:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    listing = build_kdp_listing(
        libro_nombre=libro_nombre,
        audiencia=audiencia,
        familia_rol=familia_rol,
        reto=reto,
        num_temas=num_temas,
        num_semanas=num_semanas,
    )
    save_kdp_listing(output_dir, listing)
    return listing

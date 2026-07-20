"""11b — Ensambla landing.html con Jinja2 + variantes. SIN LLM."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.sections import SECTION_ORDER, resolve_template
from src.text_utils import public_name, propuesta

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


def _font_url(family: str) -> str:
    clean = family.replace('"', "").replace("'", "").strip()
    return clean.replace(" ", "+") + ":wght@400;500;600"


def run(input: dict[str, Any]) -> dict[str, Any]:
    brief = input.get("brief") or {}
    copy = input.get("copy") or {}
    tokens = input.get("tokens") or {}
    layout = tokens.get("layout") or {}

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    nombre = public_name(brief)
    ctx_base = {
        "nombre": nombre,
        "tokens": tokens,
        "layout": layout,
        "hero": copy.get("hero") or {},
        "social": copy.get("social_proof") or {},
        "problem": copy.get("problem") or {},
        "benefits": copy.get("benefits") or {},
        "testimonials": copy.get("testimonials") or {},
        "pricing": copy.get("pricing") or {},
        "faq": copy.get("faq") or {},
        "cta": copy.get("cta_final") or {},
        "footer": copy.get("footer") or {},
    }

    parts: list[str] = []
    included: list[str] = []
    omitted: list[str] = []
    used_templates: dict[str, str] = {}

    for sec in SECTION_ORDER:
        if sec == "testimonials":
            t = copy.get("testimonials") or {}
            if t.get("omitida") or not (t.get("items") or []):
                omitted.append(sec)
                continue
        tpl_name = resolve_template(sec, layout)
        used_templates[sec] = tpl_name
        html_part = env.get_template(tpl_name).render(**ctx_base).strip()
        if not html_part:
            omitted.append(sec)
            continue
        parts.append(html_part)
        included.append(sec)

    hero_titulo = (copy.get("hero") or {}).get("titulo") or propuesta(brief)
    page = env.get_template("base.html").render(
        nombre=nombre,
        hero_titulo=hero_titulo,
        tokens=tokens,
        font_heading_url=_font_url(tokens.get("font_heading") or "Cormorant Garamond"),
        font_body_url=_font_url(tokens.get("font_body") or "Outfit"),
        body="\n".join(parts),
    )

    for sec in SECTION_ORDER:
        count = len(re.findall(rf'data-section="{sec}"', page))
        if sec in omitted:
            assert count == 0, f"Sección omitida {sec} aparece {count} veces"
        elif sec in included:
            assert count == 1, f"Sección {sec} aparece {count} veces (debe ser 1)"

    return {
        "html": page,
        "included": included,
        "omitted": omitted,
        "templates_used": used_templates,
        "path_hint": "landing.html",
    }

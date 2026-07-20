"""12 — QA: checklist + chequeos automáticos (bugs v2)."""

from __future__ import annotations

import re
from typing import Any

from src.agents.base import load_skill
from src.text_utils import public_name


def _find_dup_words(html: str) -> list[dict[str, str]]:
    hits = []
    # texto visible aproximado
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    for m in re.finditer(r"\b(\w+)\s+\1\b", text, flags=re.IGNORECASE):
        hits.append({"texto": m.group(0), "palabra": m.group(1)})
    return hits


def _btn_backgrounds(html: str) -> list[str]:
    """Colores de fondo asociados a .btn (hardcode o var)."""
    colors = []
    # reglas .btn { ... background:... }
    for m in re.finditer(r"\.btn[^{]*\{([^}]+)\}", html):
        block = m.group(1)
        bg = re.search(r"background(?:-color)?:\s*([^;]+)", block)
        if bg:
            colors.append(bg.group(1).strip())
    # inline styles on btn
    for m in re.finditer(r'class="[^"]*btn[^"]*"[^>]*style="([^"]*)"', html):
        bg = re.search(r"background(?:-color)?:\s*([^;]+)", m.group(1))
        if bg:
            colors.append(bg.group(1).strip())
    return colors


def run(input: dict[str, Any]) -> dict[str, Any]:
    html = input.get("html") or ""
    copy = input.get("copy") or {}
    brief = input.get("brief") or {}
    _ = load_skill("qa_checklist_skill.md")

    criticos: list[dict[str, Any]] = []
    sugerencias: list[str] = []
    regenerar: list[str] = []
    omisiones: list[dict[str, str]] = []
    score = 100
    bugs_v2 = {
        "copy_duplicado": "ok",
        "overlap_secciones": "ok",
        "acento_inconsistente": "ok",
        "naming_inconsistente": "ok",
        "testimonios_silenciados": "ok",
    }

    nombre = public_name(brief)

    # 1) Palabras repetidas
    dups = _find_dup_words(html)
    if dups:
        bugs_v2["copy_duplicado"] = "fail"
        for d in dups[:5]:
            criticos.append(
                {
                    "tipo": "copy_duplicado",
                    "texto": d["texto"],
                    "detalle": f"Palabra repetida: '{d['texto']}'",
                }
            )
        regenerar.append("05_benefits")
        regenerar.append("07_pricing")
        score -= 25

    # 2) Overlap CSS: absolute/fixed fuera de header
    bad_pos = []
    for m in re.finditer(
        r"(^|\n)\s*([.#]?[\w\-]+)\s*\{([^}]*)\}", html
    ):
        selector, body = m.group(2), m.group(3)
        if re.search(r"position\s*:\s*(absolute|fixed)", body, re.I):
            sel = selector.lower()
            if sel in (".top", "header", ".top.sticky") or "top" == sel.lstrip("."):
                continue
            if sel in (".top",) or "header" in sel or sel == ".top":
                continue
            # permitir solo .top (header sticky)
            if sel.lstrip(".#") == "top":
                continue
            bad_pos.append(selector)
    # sticky en .top está permitido; absolute/fixed en otras clases no
    abs_fixed = re.findall(
        r"([.#][\w\-]+)\s*\{[^}]*position\s*:\s*(absolute|fixed)[^}]*\}",
        html,
        flags=re.I,
    )
    for sel, pos in abs_fixed:
        if sel.lstrip(".#").lower() == "top":
            continue
        bad_pos.append(f"{sel}:{pos}")
    if bad_pos:
        bugs_v2["overlap_secciones"] = "fail"
        criticos.append(
            {
                "tipo": "overlap_css",
                "detalle": f"position absolute/fixed en: {', '.join(sorted(set(bad_pos)))}",
                "texto": ", ".join(sorted(set(bad_pos))),
            }
        )
        regenerar.append("11_design")
        score -= 20

    # 3) Un solo acento en botones
    colors = _btn_backgrounds(html)
    # También detectar .btn-dark u otros overrides
    if re.search(r"\.btn-dark\s*\{[^}]*background", html, re.I):
        bugs_v2["acento_inconsistente"] = "fail"
        criticos.append(
            {
                "tipo": "acento_inconsistente",
                "detalle": "Existe .btn-dark con background distinto a --accent",
                "texto": ".btn-dark",
            }
        )
        regenerar.append("11_design")
        score -= 20
    unique = set(c.lower().replace(" ", "") for c in colors)
    # aceptar solo var(--accent)
    if unique and not all("var(--accent)" in c or c == "var(--accent)" for c in unique):
        # si hay más de un valor distinto
        if len(unique) > 1 or any("var(--accent)" not in c for c in unique):
            bugs_v2["acento_inconsistente"] = "fail"
            criticos.append(
                {
                    "tipo": "acento_inconsistente",
                    "detalle": f"Backgrounds de .btn: {sorted(unique)}",
                    "texto": str(sorted(unique)),
                }
            )
            regenerar.append("11_design")
            score -= 15

    # 4) Naming: nombre_producto en title, hero brand, footer
    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = title_m.group(1) if title_m else ""
    brand = ""
    bm = re.search(r'class="brand-hero">([^<]+)<', html)
    if bm:
        brand = bm.group(1).strip()
    footer_txt = ""
    fm = re.search(r"<footer>([\s\S]*?)</footer>", html, re.I)
    if fm:
        footer_txt = re.sub(r"<[^>]+>", " ", fm.group(1))
        footer_txt = re.sub(r"\s+", " ", footer_txt).strip()

    if nombre and nombre not in title:
        bugs_v2["naming_inconsistente"] = "fail"
        criticos.append(
            {
                "tipo": "naming",
                "detalle": f"<title> no contiene nombre_producto '{nombre}'",
                "texto": title,
            }
        )
        regenerar.append("11_design")
        score -= 15
    if nombre and brand and brand != nombre:
        bugs_v2["naming_inconsistente"] = "fail"
        criticos.append(
            {
                "tipo": "naming",
                "detalle": f"Hero brand '{brand}' ≠ nombre_producto '{nombre}'",
                "texto": brand,
            }
        )
        regenerar.append("11_design")
        score -= 15
    if nombre and footer_txt and nombre not in footer_txt:
        bugs_v2["naming_inconsistente"] = "fail"
        criticos.append(
            {
                "tipo": "naming",
                "detalle": f"Footer no contiene nombre_producto '{nombre}'",
                "texto": footer_txt[:80],
            }
        )
        regenerar.append("10_footer")
        score -= 10

    # producto_interno / catálogo no debe aparecer en FAQ visible
    interno = (brief.get("producto_interno") or "").strip()
    if interno and interno != nombre and interno in html:
        # permitir solo si es substring accidental; marcar si aparece en FAQ
        faq_block = re.search(r'id="faq"[\s\S]*?</section>', html, re.I)
        if faq_block and interno in faq_block.group(0):
            bugs_v2["naming_inconsistente"] = "fail"
            criticos.append(
                {
                    "tipo": "naming",
                    "detalle": f"Nombre interno '{interno}' filtrado a FAQ",
                    "texto": interno,
                }
            )
            regenerar.append("08_faq")
            score -= 20

    # 5) Testimonios: omisión explícita
    testimonials = copy.get("testimonials") or {}
    if testimonials.get("omitida"):
        omisiones.append(
            {
                "seccion": "testimonials",
                "motivo": testimonials.get("motivo") or "sin data real",
            }
        )
        if 'id="testimonios"' in html:
            bugs_v2["testimonios_silenciados"] = "fail"
            criticos.append(
                {
                    "tipo": "testimonios",
                    "detalle": "omitida=true pero la sección aparece en HTML",
                    "texto": "testimonios",
                }
            )
            regenerar.append("11_design")
            score -= 10
        else:
            sugerencias.append(
                f"Testimonios omitidos (explícito): {testimonials.get('motivo')}"
            )
            bugs_v2["testimonios_silenciados"] = "ok_omitida_explicita"
    elif not (testimonials.get("items") or []) and 'id="testimonios"' not in html:
        bugs_v2["testimonios_silenciados"] = "fail"
        criticos.append(
            {
                "tipo": "testimonios",
                "detalle": "Sección ausente sin omitida:true en copy",
                "texto": "testimonials",
            }
        )
        regenerar.append("06_testimonials")
        score -= 15

    # Secciones esperadas
    expected = ["hero", "problema", "beneficios", "precio", "faq"]
    if not testimonials.get("omitida") and (testimonials.get("items") or []):
        expected.append("testimonios")
    present = re.findall(r'<section[^>]*id="([^"]+)"', html)
    for sec in expected:
        if sec not in present and not (sec == "hero" and 'class="hero' in html):
            if sec == "hero" and re.search(r'id="hero"|class="[^"]*hero', html):
                continue
            criticos.append(
                {
                    "tipo": "seccion_faltante",
                    "detalle": f"Falta <section id=\"{sec}\"> sin omisión registrada",
                    "texto": sec,
                }
            )
            score -= 10

    # CTA genérico
    hero = copy.get("hero") or {}
    if (hero.get("cta") or "").lower() in ("enviar", "click aquí", "click aqui"):
        criticos.append({"tipo": "cta", "detalle": "CTA genérico", "texto": hero.get("cta")})
        regenerar.append("02_hero")
        score -= 15

    if "viewport" not in html:
        criticos.append({"tipo": "mobile", "detalle": "Sin meta viewport", "texto": ""})
        regenerar.append("11_design")
        score -= 15

    score = max(0, min(100, score))
    return {
        "score": score,
        "criticos": criticos,
        "sugerencias": sugerencias,
        "regenerar": sorted(set(regenerar)),
        "omisiones": omisiones,
        "bugs_v2": bugs_v2,
        "n_sections": len(re.findall(r"<section", html, flags=re.I)),
    }

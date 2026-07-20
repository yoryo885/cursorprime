"""12 — QA: checklist + duplicados + bugs v2/v4."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from src.agents.base import load_skill
from src.sections import SECTION_ORDER
from src.text_utils import public_name


def _find_dup_words(html: str) -> list[dict[str, str]]:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return [
        {"texto": m.group(0), "palabra": m.group(1)}
        for m in re.finditer(r"\b(\w+)\s+\1\b", text, flags=re.IGNORECASE)
    ]


def _section_text(html: str, sec: str) -> str:
    m = re.search(
        rf'data-section="{sec}"[^>]*>([\s\S]*?)(?=data-section=|</body>)',
        html,
        flags=re.I,
    )
    if not m:
        return ""
    t = re.sub(r"<[^>]+>", " ", m.group(1))
    return re.sub(r"\s+", " ", t).strip()


def _similarity(a: str, b: str) -> float:
    wa = a.lower().split()[:80]
    wb = b.lower().split()[:80]
    if not wa or not wb:
        return 0.0
    sa, sb = set(wa), set(wb)
    return len(sa & sb) / max(len(sa | sb), 1)


def run(input: dict[str, Any]) -> dict[str, Any]:
    html = input.get("html") or ""
    copy = input.get("copy") or {}
    brief = input.get("brief") or {}
    assemble_meta = input.get("assemble_meta") or {}
    _ = load_skill("qa_checklist_skill.md")

    criticos: list[dict[str, Any]] = []
    sugerencias: list[str] = []
    regenerar: list[str] = []
    omisiones: list[dict[str, str]] = []
    section_counts: dict[str, int] = {}
    score = 100
    bugs_v2 = {
        "copy_duplicado": "ok",
        "overlap_secciones": "ok",
        "acento_inconsistente": "ok",
        "naming_inconsistente": "ok",
        "testimonios_silenciados": "ok",
        "secciones_duplicadas": "ok",
    }

    nombre = public_name(brief)

    # Conteos data-section
    found = re.findall(r'data-section="([^"]+)"', html)
    counts = Counter(found)
    for sec in SECTION_ORDER:
        c = counts.get(sec, 0)
        section_counts[sec] = c
        omitted_legit = False
        if sec == "testimonials":
            t = copy.get("testimonials") or {}
            if t.get("omitida") or not (t.get("items") or []):
                omitted_legit = True
        if omitted_legit:
            if c != 0:
                bugs_v2["secciones_duplicadas"] = "fail"
                criticos.append(
                    {
                        "tipo": "seccion_omitida_presente",
                        "detalle": f"{sec} omitida pero aparece {c} veces",
                        "texto": sec,
                    }
                )
                regenerar.append("11b_assemble")
                score -= 20
            else:
                omisiones.append(
                    {
                        "seccion": sec,
                        "motivo": (copy.get("testimonials") or {}).get("motivo")
                        or "sin data real",
                    }
                )
                bugs_v2["testimonios_silenciados"] = "ok_omitida_explicita"
        else:
            if c == 0:
                criticos.append(
                    {
                        "tipo": "seccion_faltante",
                        "detalle": f"Falta data-section={sec}",
                        "texto": sec,
                    }
                )
                regenerar.append("11b_assemble")
                score -= 10
            elif c > 1:
                bugs_v2["secciones_duplicadas"] = "fail"
                criticos.append(
                    {
                        "tipo": "seccion_duplicada",
                        "detalle": f"{sec} aparece {c} veces (debe ser 1)",
                        "texto": sec,
                    }
                )
                regenerar.append("11b_assemble")
                score -= 25

    # Similitud entre pares (red de seguridad)
    texts = {sec: _section_text(html, sec) for sec in SECTION_ORDER if section_counts.get(sec, 0)}
    secs = list(texts.keys())
    for i in range(len(secs)):
        for j in range(i + 1, len(secs)):
            a, b = secs[i], secs[j]
            # hero vs cta_final puede ser similar a propósito — avisar suave
            sim = _similarity(texts[a], texts[b])
            if sim >= 0.7 and {a, b} != {"hero", "cta_final"}:
                bugs_v2["secciones_duplicadas"] = "fail"
                criticos.append(
                    {
                        "tipo": "texto_duplicado_secciones",
                        "detalle": f"{a} ≈ {b} ({sim:.0%})",
                        "texto": f"{a}/{b}",
                    }
                )
                score -= 15
            elif sim >= 0.7 and {a, b} == {"hero", "cta_final"}:
                sugerencias.append("Hero y CTA final comparten mensaje (esperado).")

    # Palabras repetidas
    dups = _find_dup_words(html)
    if dups:
        bugs_v2["copy_duplicado"] = "fail"
        for d in dups[:5]:
            criticos.append({"tipo": "copy_duplicado", "texto": d["texto"], "detalle": d["texto"]})
        regenerar.extend(["05_benefits", "07_pricing"])
        score -= 25

    # absolute/fixed fuera de header
    for sel, pos in re.findall(
        r"([.#][\w\-]+)\s*\{[^}]*position\s*:\s*(absolute|fixed)[^}]*\}", html, flags=re.I
    ):
        if sel.lstrip(".#").lower() in ("top",):
            continue
        bugs_v2["overlap_secciones"] = "fail"
        criticos.append(
            {"tipo": "overlap_css", "detalle": f"{sel} position:{pos}", "texto": sel}
        )
        regenerar.append("11b_assemble")
        score -= 20

    # Animaciones prohibidas en MVP
    if re.search(r"IntersectionObserver|fade-in-up|scroll-reveal|translateY\s*\(", html, re.I):
        if re.search(r"opacity\s*:\s*0", html, re.I):
            bugs_v2["overlap_secciones"] = "fail"
            criticos.append(
                {
                    "tipo": "animacion_scroll",
                    "detalle": "Animación de entrada detectada (riesgo de overlap)",
                    "texto": "opacity:0 / translateY",
                }
            )
            regenerar.append("11b_assemble")
            score -= 15

    # Acento único
    if re.search(r"\.btn-dark\s*\{", html, re.I):
        bugs_v2["acento_inconsistente"] = "fail"
        criticos.append({"tipo": "acento_inconsistente", "detalle": ".btn-dark", "texto": ".btn-dark"})
        regenerar.append("11b_assemble")
        score -= 20
    btn_bgs = re.findall(r"\.btn[^{]*\{[^}]*background(?:-color)?:\s*([^;]+)", html)
    uniq = {c.strip().lower().replace(" ", "") for c in btn_bgs}
    if uniq and any("var(--accent)" not in c for c in uniq):
        bugs_v2["acento_inconsistente"] = "fail"
        criticos.append(
            {"tipo": "acento_inconsistente", "detalle": str(sorted(uniq)), "texto": str(sorted(uniq))}
        )
        regenerar.append("11b_assemble")
        score -= 15

    # Naming
    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = title_m.group(1) if title_m else ""
    brand_m = re.search(r'class="brand-hero">([^<]+)<', html)
    brand = brand_m.group(1).strip() if brand_m else ""
    if nombre and nombre not in title:
        bugs_v2["naming_inconsistente"] = "fail"
        criticos.append({"tipo": "naming", "detalle": "title", "texto": title})
        score -= 15
    if nombre and brand and brand != nombre:
        bugs_v2["naming_inconsistente"] = "fail"
        criticos.append({"tipo": "naming", "detalle": "hero brand", "texto": brand})
        score -= 15
    interno = (brief.get("producto_interno") or "").strip()
    if interno and interno != nombre:
        faq_m = re.search(r'data-section="faq"[\s\S]*?(?=data-section=|</body>)', html)
        if faq_m and interno in faq_m.group(0):
            bugs_v2["naming_inconsistente"] = "fail"
            criticos.append({"tipo": "naming", "detalle": "interno en FAQ", "texto": interno})
            regenerar.append("08_faq")
            score -= 20

    # Testimonios sin omitida
    t = copy.get("testimonials") or {}
    if not t.get("omitida") and not (t.get("items") or []) and section_counts.get("testimonials", 0) == 0:
        bugs_v2["testimonios_silenciados"] = "fail"
        criticos.append(
            {"tipo": "testimonios", "detalle": "ausente sin omitida:true", "texto": "testimonials"}
        )
        regenerar.append("06_testimonials")
        score -= 15

    if assemble_meta.get("omitted"):
        for s in assemble_meta["omitted"]:
            if not any(o["seccion"] == s for o in omisiones):
                omisiones.append({"seccion": s, "motivo": "omitida en assemble"})

    score = max(0, min(100, score))
    return {
        "score": score,
        "criticos": criticos,
        "sugerencias": sugerencias,
        "regenerar": sorted(set(regenerar)),
        "omisiones": omisiones,
        "bugs_v2": bugs_v2,
        "section_counts": section_counts,
        "n_sections": sum(1 for v in section_counts.values() if v > 0),
    }

"""12 — QA contra qa_checklist_skill.md"""

from __future__ import annotations

import re
from typing import Any

from src.agents.base import load_skill


def run(input: dict[str, Any]) -> dict[str, Any]:
    html = input.get("html") or ""
    copy = input.get("copy") or {}
    _ = load_skill("qa_checklist_skill.md")

    criticos: list[str] = []
    sugerencias: list[str] = []
    regenerar: list[str] = []
    score = 100

    hero = copy.get("hero") or {}
    if not hero.get("titulo") or not hero.get("cta"):
        criticos.append("Hero incompleto (falta título o CTA)")
        regenerar.append("02_hero")
        score -= 25
    cta = (hero.get("cta") or "").lower()
    if cta in ("enviar", "click aquí", "click aqui", "submit"):
        criticos.append("CTA genérico en hero")
        regenerar.append("02_hero")
        score -= 20

    # Secciones en HTML
    section_ids = re.findall(r'<section[^>]*id="([^"]+)"', html)
    n_sections = len(re.findall(r"<section", html, flags=re.I))
    if n_sections > 8:
        sugerencias.append(f"Demasiadas secciones ({n_sections}): simplificar")
        score -= 10

    pricing = copy.get("pricing") or {}
    if not pricing.get("precio"):
        criticos.append("Precio no visible")
        regenerar.append("07_pricing")
        score -= 20

    tests = (copy.get("testimonials") or {}).get("items") or []
    nota = (copy.get("testimonials") or {}).get("nota") or ""
    if tests and "invent" in nota.lower():
        criticos.append("Testimonios marcados como inventados")
        regenerar.append("06_testimonials")
        score -= 25
    if not tests and "sin testimonios" in nota.lower():
        sugerencias.append("Sin testimonios reales: OK (no inventar). Agregar cuando existan.")

    # Botón con clase accent (debe existir .btn)
    if 'class="btn"' not in html and "class='btn'" not in html:
        criticos.append("Botón CTA no destacado / ausente")
        regenerar.append("11_design")
        score -= 15

    # Viewport mobile
    if "viewport" not in html:
        criticos.append("Sin meta viewport (mobile)")
        regenerar.append("11_design")
        score -= 15

    # Más de un h1
    if len(re.findall(r"<h1", html, flags=re.I)) > 1:
        sugerencias.append("Más de un H1: unificar mensaje principal")
        score -= 5

    # Social proof confianza baja
    sp = copy.get("social_proof") or {}
    if sp.get("confianza") == "baja":
        sugerencias.append("Social proof con confianza baja: validar cifra o quitar claim")
        score -= 5

    if "problema" not in section_ids and "problem" not in html.lower():
        sugerencias.append("Sección problema poco visible")
        score -= 5

    score = max(0, min(100, score))
    return {
        "score": score,
        "criticos": criticos,
        "sugerencias": sugerencias,
        "regenerar": sorted(set(regenerar)),
        "n_sections": n_sections,
    }

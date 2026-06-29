"""Traduce hallazgos técnicos a lenguaje claro para dueños de negocio local."""

from __future__ import annotations

import re

# title pattern (lower) -> (título cliente, detalle cliente, acción concreta)
FINDING_MAP: list[tuple[str, str, str, str]] = [
    (
        r"meta description|sin meta",
        "Cuando te buscan en Google, no aparece un mensaje claro",
        "Google muestra un texto genérico o incompleto. Eso hace que menos personas hagan clic.",
        "Redactar 2–3 frases que digan qué haces, dónde estás y por qué contactarte.",
    ),
    (
        r"sin h1|h1 claro",
        "Al entrar a tu web no se entiende rápido qué ofreces",
        "El visitante tarda en descubrir de qué trata tu negocio.",
        "Poner un titular grande y claro arriba: qué haces y para quién.",
    ),
    (
        r"imagen.*sin alt|sin alt",
        "Algunas fotos no ayudan a que Google entienda tu negocio",
        "Las imágenes no tienen descripción; Google y personas con discapacidad visual pierden contexto.",
        "Describir cada foto importante en pocas palabras (ej.: «Consultorio odontológico en Providencia»).",
    ),
    (
        r"sin cta|ctas detectados",
        "No hay un botón claro para que te contacten",
        "Quien entra no ve de inmediato cómo agendar, escribir o llamar.",
        "Agregar un botón visible arriba: «Agenda hora», «Escríbenos por WhatsApp» o «Llámanos».",
    ),
    (
        r"un solo cta",
        "Solo hay una forma de contactarte en la web",
        "Algunos clientes prefieren WhatsApp, otros teléfono o formulario.",
        "Sumar una segunda opción de contacto fácil de ver.",
    ),
    (
        r"alternativas|competidor|posicionamiento",
        "No se ve por qué elegirte frente a otros similares",
        "Tu web no explica qué te hace diferente de la competencia de la zona.",
        "Añadir una sección corta: «Por qué elegirnos» con 3 razones concretas.",
    ),
    (
        r"schema|json-ld|rich results",
        "Google no tiene datos completos de tu negocio",
        "Faltan datos que ayudan a mostrar horario, dirección o preguntas frecuentes en Google.",
        "Completar ficha de Google Maps y datos de contacto visibles en la web.",
    ),
    (
        r"viewport|móvil|mobile",
        "La web no se ve bien en celular",
        "Muchos clientes te buscan desde el teléfono; una mala experiencia hace que se vayan.",
        "Revisar que botones, textos e imágenes se lean bien en pantalla chica.",
    ),
]

PRIORIDAD_PESO = {
    "25%": "Alta",
    "20%": "Alta",
    "15%": "Media",
    "10%": "Complementaria",
}

TIPO_NEGOCIO_ES = {
    "local_business": "Negocio local",
    "ecommerce": "Tienda online",
    "saas": "Software / servicio digital",
    "general": "Negocio",
}

SEVERIDAD_CLIENTE = {
    "critical": "Urgente",
    "high": "Importante",
    "medium": "A mejorar",
    "low": "Opcional",
}


def _match_finding(title: str, detail: str) -> tuple[str, str, str] | None:
    blob = f"{title} {detail}".lower()
    for pattern, ct, cd, action in FINDING_MAP:
        if re.search(pattern, blob):
            return ct, cd, action
    return None


def humanize_finding(finding: dict) -> dict:
    """Añade client_title, client_detail, client_action sin borrar campos técnicos."""
    title = finding.get("title") or ""
    detail = finding.get("detail") or ""
    mapped = _match_finding(title, detail)
    if mapped:
        ct, cd, action = mapped
    else:
        ct = title
        cd = detail
        action = detail if detail else title
    return {
        **finding,
        "client_title": ct,
        "client_detail": cd,
        "client_action": action,
    }


def dedupe_findings(findings: list[dict]) -> list[dict]:
    """Elimina hallazgos repetidos por título cliente."""
    seen: set[str] = set()
    out: list[dict] = []
    for f in findings:
        h = humanize_finding(f)
        key = h["client_title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


def humanize_quick_wins(findings: list[dict], limit: int = 5) -> list[str]:
    """Acciones concretas en lenguaje simple, sin duplicados."""
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_f = sorted(findings, key=lambda x: order.get(x.get("severity", "low"), 9))
    seen: set[str] = set()
    wins: list[str] = []
    for f in sorted_f:
        h = humanize_finding(f) if "client_action" not in f else f
        action = h.get("client_action") or h.get("client_title") or ""
        if not action or action.lower() in seen:
            continue
        seen.add(action.lower())
        wins.append(action)
        if len(wins) >= limit:
            break
    return wins


def resumen_ejecutivo(score: int, grade: str, brand: str) -> str:
    g = {"A": "muy bien", "B": "bien", "C": "regular", "D": "bajo", "F": "muy bajo"}.get(grade, "regular")
    if score < 60:
        return (
            f"Revisamos la presencia online de **{brand}**. "
            f"Tu nota es **{score}/100** — hay oportunidades claras para atraer más clientes desde Google y tu web. "
            "Abajo te explicamos qué significa cada punto y qué puedes hacer esta semana."
        )
    if score < 75:
        return (
            f"**{brand}** tiene una base **{g}** ({score}/100), pero compites con negocios que probablemente "
            "lo hacen mejor en web y Google. Estas mejoras pueden sumar más consultas sin gastar en publicidad."
        )
    return (
        f"**{brand}** va **{g}** ({score}/100). Con algunos ajustes puntuales puedes convertir más visitas en clientes."
    )

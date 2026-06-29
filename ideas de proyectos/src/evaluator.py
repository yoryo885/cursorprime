"""Motor de evaluación — heurísticas + informe."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.config import CONSTITUTION_PATH, load_json


def _tipo_negocio(idea: dict) -> str:
    texto = " ".join(
        str(idea.get(k) or "")
        for k in ("modelo_negocio", "problema", "titulo", "notas")
    ).lower()
    if any(w in texto for w in ("saas", "software", "suscripcion", "plataforma")):
        return "saas"
    if any(w in texto for w in ("whatsapp", "bot", "local", "tienda", "pedido")):
        return "servicio_local"
    if any(w in texto for w in ("marketplace", "mercado libre", "dropship")):
        return "ecommerce"
    return "general"


def _margen_por_tipo(tipo: str) -> dict[str, Any]:
    rangos = {
        "saas": {"min": 60, "max": 85, "point": 72, "unidad": "margen_bruto_pct"},
        "servicio_local": {"min": 25, "max": 55, "point": 38, "unidad": "margen_neto_pct"},
        "ecommerce": {"min": 10, "max": 35, "point": 20, "unidad": "margen_neto_pct"},
        "general": {"min": 15, "max": 40, "point": 25, "unidad": "margen_neto_pct"},
    }
    return rangos.get(tipo, rangos["general"])


def _score_idea(idea: dict, tipo: str) -> tuple[int, float, list[str]]:
    score = 50
    warnings: list[str] = []
    confidence = 0.55

    if len(str(idea.get("problema") or "")) > 40:
        score += 12
    else:
        warnings.append("Problema poco definido")
        confidence -= 0.1

    if idea.get("cliente_objetivo") or idea.get("usuario_final"):
        score += 8
    else:
        warnings.append("Cliente objetivo no claro")

    if idea.get("modelo_negocio"):
        score += 10
    else:
        warnings.append("Modelo de negocio ausente")
        confidence -= 0.15

    if idea.get("hipotesis"):
        score += 5
        confidence += 0.05

    if idea.get("mercado"):
        score += 5

    if tipo == "servicio_local":
        score += 8  # dolor operativo claro suele ser viable MVP
    if tipo == "ecommerce":
        score -= 5
        warnings.append("E-commerce: validar márgenes reales antes de escalar")

    if not idea.get("urls_referencia") and not idea.get("integraciones"):
        warnings.append("Sin fuentes externas — confidence reducida")
        confidence -= 0.1

    score = max(0, min(100, score))
    confidence = max(0.3, min(0.85, confidence))
    return score, confidence, warnings


def _veredicto(score: int) -> str:
    if score >= 65:
        return "viable"
    if score >= 40:
        return "condicional"
    return "descartar"


def _escala(tipo: str, score: int) -> dict[str, Any]:
    notas = {
        "saas": "Escala bien si el onboarding es self-service",
        "servicio_local": "Escala por nicho (mismo dolor, distintos rubros)",
        "ecommerce": "Escala limitada si depende de proveedor o márgenes finos",
        "general": "Revisar cuellos de botella manuales",
    }
    sirve = score >= 45 and tipo != "ecommerce" or (tipo == "ecommerce" and score >= 55)
    return {"sirve": sirve, "nota": notas.get(tipo, notas["general"])}


def _riesgos(tipo: str, idea: dict) -> list[dict[str, str]]:
    base = [
        {"nivel": "medio", "riesgo": "Mercado no validado con datos reales"},
        {"nivel": "medio", "riesgo": "MVP más largo de lo estimado"},
    ]
    if tipo == "servicio_local":
        base.insert(0, {"nivel": "bajo", "riesgo": "Dependencia WhatsApp/Meta"})
    if tipo == "ecommerce":
        base.insert(0, {"nivel": "alto", "riesgo": "Márgenes y stock del proveedor"})
    if "semi" in str(idea.get("modelo_negocio") or "").lower():
        base.append({"nivel": "bajo", "riesgo": "Semi-auto reduce riesgo inicial"})
    return base[:3]


def _siguiente_paso(veredicto: str, tipo: str, idea: dict) -> str:
    if veredicto == "descartar":
        return "Pivotar o entrevistar 5 clientes potenciales antes de seguir"
    if veredicto == "condicional":
        return "Validar margen y disposición a pagar con 3 clientes del nicho"
    pasos = {
        "servicio_local": "MVP: bot WhatsApp + cola de pedidos en 2 semanas",
        "saas": "MVP: landing + waitlist + entrevistas con 10 usuarios",
        "ecommerce": "MVP: 10 SKUs, calcular margen real, semi-auto",
    }
    return pasos.get(tipo, "Definir MVP en 1 página y probar en 2 semanas")


def evaluate(idea: dict, slug: str) -> dict[str, Any]:
    constitution = load_json(CONSTITUTION_PATH, {})
    tipo = _tipo_negocio(idea)
    score, confidence, warnings = _score_idea(idea, tipo)
    veredicto = _veredicto(score)
    margen = _margen_por_tipo(tipo)

    return {
        "slug": slug,
        "titulo": idea.get("titulo") or idea.get("nombre") or slug,
        "evaluado_at": datetime.now(timezone.utc).isoformat(),
        "tipo_negocio": tipo,
        "veredicto": veredicto,
        "score": score,
        "confidence": round(confidence, 2),
        "margen": margen,
        "escala": _escala(tipo, score),
        "riesgos": _riesgos(tipo, idea),
        "siguiente_paso": _siguiente_paso(veredicto, tipo, idea),
        "warnings": warnings,
        "constitution_version": constitution.get("version", 1),
    }


def render_informe(idea: dict, result: dict[str, Any]) -> str:
    m = result["margen"]
    lines = [
        f"# Evaluación — {result['titulo']}",
        "",
        f"**Veredicto:** {result['veredicto'].upper()} · Score {result['score']}/100 · "
        f"Confianza {int(result['confidence'] * 100)}%",
        "",
        "## Problema",
        str(idea.get("problema") or "—"),
        "",
        "## Margen estimado",
        f"- Rango: **{m['min']}% – {m['max']}%** (punto medio {m['point']}%)",
        f"- Tipo: {result['tipo_negocio']}",
        "",
        "## ¿Escala?",
        f"- {'Sí' if result['escala']['sirve'] else 'Con reservas'} — {result['escala']['nota']}",
        "",
        "## Riesgos",
    ]
    for r in result["riesgos"]:
        lines.append(f"- [{r['nivel']}] {r['riesgo']}")
    lines.extend(["", "## Siguiente paso", "", result["siguiente_paso"], ""])
    if result["warnings"]:
        lines.extend(["## Advertencias", ""])
        lines.extend(f"- {w}" for w in result["warnings"])
    lines.extend(
        [
            "",
            "---",
            "PDF: pasar este archivo a **libros a entender** (`--solo-pdf`).",
        ]
    )
    return "\n".join(lines)

"""Paletas preset + recomendación automática."""

from __future__ import annotations

from src.config import load_json, preguntas_path


def load_paletas() -> dict:
    spec = load_json(preguntas_path(), {}) or {}
    return spec.get("paletas_preset") or {}


def recomendar_clima(respuestas: dict) -> str:
    clima = (respuestas.get("clima_color") or "auto").lower().strip()
    if clima in ("cálido", "calido", "frío", "frio", "neutro", "oscuro"):
        return {"cálido": "calido", "calido": "calido", "frío": "frio", "frio": "frio"}.get(clima, clima)
    tono = (respuestas.get("tono") or "").lower()
    estilo = (respuestas.get("estilo") or respuestas.get("estilo_preferido") or "").lower()
    if estilo == "oferta" or tono == "directo":
        return "frio"
    if estilo == "tienda":
        return "neutro"
    return "neutro"


def elegir_paleta(respuestas: dict) -> dict:
    presets = load_paletas()
    clima = recomendar_clima(respuestas)
    grupo = presets.get(clima) or presets.get("neutro") or {}
    choice = (respuestas.get("paleta") or "auto").upper().strip()
    if choice not in ("A", "B", "C"):
        choice = "A"
    pal = dict(grupo.get(choice) or next(iter(grupo.values()), {}))
    pal["id"] = choice
    pal["clima"] = clima
    return pal


def formato_chat_paletas(respuestas: dict | None = None) -> str:
    """Texto para el agente: 3 opciones A/B/C con la recomendada."""
    r = respuestas or {}
    clima = recomendar_clima(r)
    grupo = load_paletas().get(clima) or {}
    lines = [f"Clima recomendado: **{clima}** → elige paleta:", ""]
    for key in ("A", "B", "C"):
        p = grupo.get(key) or {}
        mark = " ← recomendada" if key == "A" else ""
        lines.append(
            f"- **{key}. {p.get('nombre', key)}**{mark}: "
            f"ink `{p.get('ink')}` · paper `{p.get('paper')}` · "
            f"accent `{p.get('accent')}` · muted `{p.get('muted')}`"
        )
    lines.append("")
    lines.append("Responde: `A` / `B` / `C` / `auto`")
    return "\n".join(lines)

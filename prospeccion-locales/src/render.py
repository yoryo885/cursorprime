"""Render leads → JSON + markdown."""

from __future__ import annotations

from datetime import datetime, timezone


def render_md(payload: dict) -> str:
    lines = [
        f"# Leads — {payload.get('rubro', '')} · {payload.get('ciudad', '')}",
        f"",
        f"Generado: {payload.get('generado_legible', '')} · Modo: **{payload.get('modo', '')}**",
        f"Viables (score ≥50): **{payload.get('viables', 0)}** / {payload.get('total', 0)}",
        f"",
        "| Score | Negocio | Señales | Web | Teléfono |",
        "|------:|---------|---------|-----|----------|",
    ]
    for L in payload.get("leads", []):
        sen = ", ".join(L.get("senales", []))
        web = L.get("web") or "—"
        tel = L.get("telefono") or "—"
        mark = "✓" if L.get("viable") else "·"
        lines.append(
            f"| {L.get('score', 0)} {mark} | {L.get('nombre', '')} | {sen} | {web[:30]} | {tel} |"
        )
    lines += ["", "## Uso", "", "1. Contactar por WhatsApp con 1 hallazgo real", "2. Ofrecer informe (Paso 1 Presencia digital)", ""]
    return "\n".join(lines)


def build_payload(rubro: str, ciudad: str, modo: str, leads: list[dict]) -> dict:
    viables = sum(1 for L in leads if L.get("viable"))
    now = datetime.now(timezone.utc)
    return {
        "rubro": rubro,
        "ciudad": ciudad,
        "modo": modo,
        "generado_at": now.isoformat(),
        "generado_legible": now.strftime("%d/%m/%Y %H:%M UTC"),
        "total": len(leads),
        "viables": viables,
        "leads": sorted(leads, key=lambda x: x.get("score", 0), reverse=True),
    }

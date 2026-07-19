"""Propone 3 estilos de landing según respuestas."""

from __future__ import annotations

from src.config import save_json
from src.types import AgentResult, PipelineContext

ESTILOS = [
    {
        "id": "editorial",
        "nombre": "Editorial hero",
        "cuando": "Marca seria, PDF/guías, profesional",
        "look": "Foto lifestyle full-bleed + marca grande + 1 CTA (como Vértice Pro imagen 6)",
        "mejor_si": ["editorial", "profesional", "pdf", "curso", "guia"],
    },
    {
        "id": "mockup",
        "nombre": "Mockup producto",
        "cuando": "Quieres que se vea el PDF/app en tablet",
        "look": "Producto centrado, fondo claro, ficha de compra debajo",
        "mejor_si": ["mockup", "digital", "ebook", "template"],
    },
    {
        "id": "oferta",
        "nombre": "Oferta directa",
        "cuando": "Tráfico de ads, quieres cerrar rápido",
        "look": "Promesa fuerte, bullets, precio, FAQ, CTA repetido",
        "mejor_si": ["directo", "ads", "oferta", "lanzamiento"],
    },
]


def _recomendar(respuestas: dict) -> str:
    pref = (respuestas.get("estilo_preferido") or "").lower().strip()
    if pref in ("editorial", "mockup", "oferta"):
        return pref
    blob = " ".join(str(v).lower() for v in respuestas.values())
    tono = (respuestas.get("tono") or "").lower()
    if tono == "directo" or "ads" in blob:
        return "oferta"
    if "mockup" in pref or "tablet" in blob:
        return "mockup"
    return "editorial"


class ExamplesAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        r = ctx.respuestas
        recomendado = _recomendar(r)
        ctx.ejemplo = r.get("ejemplo_elegido") or recomendado

        lines = [
            f"# Ejemplos de landing — {r.get('marca', ctx.slug)}",
            "",
            f"**Producto:** {r.get('producto', '—')}",
            f"**Cliente:** {r.get('cliente', '—')}",
            "",
            f"**Recomendado para ti:** `{recomendado}`",
            "",
        ]
        for i, e in enumerate(ESTILOS, 1):
            mark = " ← recomendado" if e["id"] == recomendado else ""
            lines += [
                f"## {i}. {e['nombre']} (`{e['id']}`){mark}",
                f"- **Cuándo:** {e['cuando']}",
                f"- **Look:** {e['look']}",
                "",
            ]
        lines += [
            "---",
            "Elige con: `--ejemplo editorial|mockup|oferta`",
            "O escribe en respuestas.json: `\"ejemplo_elegido\": \"editorial\"`",
        ]

        md = "\n".join(lines)
        out_md = ctx.paths["output"] / "ejemplos.md"
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(md, encoding="utf-8")

        payload = {"recomendado": recomendado, "elegido": ctx.ejemplo, "estilos": ESTILOS}
        save_json(ctx.paths["meta"] / "ejemplos.json", payload)

        print(f"     recomendado: {recomendado} · usando: {ctx.ejemplo}")
        return AgentResult(ok=True, artifacts=[str(out_md)], notes="3 ejemplos")

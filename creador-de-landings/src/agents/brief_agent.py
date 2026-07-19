"""Arma brief JSON + markdown."""

from __future__ import annotations

from src.config import save_json
from src.types import AgentResult, PipelineContext


class BriefAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        r = ctx.respuestas
        ejemplo = ctx.ejemplo or "editorial"
        brief = {
            "marca": r.get("marca") or ctx.slug,
            "producto": r.get("producto") or "",
            "cliente": r.get("cliente") or "",
            "promesa": r.get("promesa") or "",
            "cta": r.get("cta") or "Comprar",
            "precio": r.get("precio") or "",
            "tono": r.get("tono") or "editorial",
            "estilo": ejemplo,
            "beneficios": [
                f"Hecho para {r.get('cliente') or 'profesionales'}",
                r.get("promesa") or "Resultado claro en poco tiempo",
                "Descarga al instante" if "pdf" in (r.get("producto") or "").lower() or "guía" in (r.get("producto") or "").lower() else "Empiezas hoy",
            ],
            "testimonios": [
                {"texto": "[PENDIENTE: testimonio real]", "autor": "Cliente"},
            ],
            "faq": [
                {"q": "¿Qué recibo?", "a": r.get("producto") or "El producto digital listo para usar."},
                {"q": "¿Para quién es?", "a": r.get("cliente") or "Profesionales que quieren aplicar ideas."},
                {"q": "¿Cómo lo recibo?", "a": "Descarga inmediata tras la compra."},
            ],
        }
        save_json(ctx.paths["brief"], brief)

        md = [
            f"# Landing brief — {brief['marca']}",
            "",
            f"- **Estilo:** {brief['estilo']}",
            f"- **Headline base:** {brief['promesa'] or brief['producto']}",
            f"- **CTA:** {brief['cta']}",
            f"- **Precio:** {brief['precio'] or '—'}",
            "",
            "## Beneficios",
        ]
        for b in brief["beneficios"]:
            md.append(f"- {b}")
        md += ["", "## FAQ"]
        for f in brief["faq"]:
            md.append(f"**{f['q']}** — {f['a']}")

        path_md = ctx.paths["output"] / "brief.md"
        path_md.write_text("\n".join(md), encoding="utf-8")
        return AgentResult(ok=True, artifacts=[str(ctx.paths["brief"]), str(path_md)])

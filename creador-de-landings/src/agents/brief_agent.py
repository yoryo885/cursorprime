"""Arma brief JSON + markdown (incluye catálogo multi-producto)."""

from __future__ import annotations

from src.catalog import ensure_catalog, guias_from_catalog, roles_from_catalog, serie_from_catalog
from src.config import save_json
from src.learning import aplicar_al_brief
from src.types import AgentResult, PipelineContext


class BriefAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        r = ctx.respuestas
        ejemplo = ctx.ejemplo or "editorial"
        catalog = ensure_catalog(ctx.slug)
        guias = guias_from_catalog(catalog)
        roles = roles_from_catalog(catalog)
        serie = serie_from_catalog(catalog)

        brief = {
            "marca": r.get("marca") or ctx.slug,
            "producto": r.get("producto") or "Guías PDF para tu rol profesional",
            "cliente": r.get("cliente") or "Profesionales por oficio",
            "promesa": r.get("promesa")
            or "Ideas de libros aplicadas a tu rol — elige tu guía",
            "cta": r.get("cta") or "Ver colección",
            "precio": r.get("precio") or "",
            "tono": r.get("tono") or "editorial",
            "estilo": ejemplo,
            "serie_libros": serie,
            "roles": roles,
            "productos": guias,
            "mostrar_catalogo": True,
            "beneficios": [
                "Varias guías: elige libro × tu rol",
                "Plan de acción de 10 semanas por guía",
                "Descarga al instante (PDF)",
            ],
            "testimonios": [
                {"texto": "[PENDIENTE: testimonio real]", "autor": "Cliente"},
            ],
            "faq": [
                {
                    "q": "¿Solo hay una guía?",
                    "a": "No. Hay varias combinaciones libro × rol. Algunas ya disponibles y otras próximamente.",
                },
                {
                    "q": "¿Qué recibo?",
                    "a": "Un PDF adaptado a tu oficio, con plan de 10 semanas.",
                },
                {
                    "q": "¿Cómo elijo?",
                    "a": "Filtra por tu rol o mira la colección completa abajo.",
                },
                {
                    "q": "¿Cómo lo recibo?",
                    "a": "Descarga inmediata tras la compra.",
                },
            ],
        }
        brief = aplicar_al_brief(brief)
        save_json(ctx.paths["brief"], brief)

        md = [
            f"# Landing brief — {brief['marca']}",
            "",
            f"- **Estilo:** {brief['estilo']}",
            f"- **Promesa:** {brief['promesa']}",
            f"- **CTA:** {brief['cta']}",
            f"- **Productos en catálogo:** {len(guias)}",
            "",
            "## Serie (libros)",
        ]
        for s in serie:
            md.append(f"- {s.get('titulo')} ({s.get('slug')})")
        md += ["", "## Guías (libro × rol)"]
        for g in guias:
            estado = "disponible" if g.get("disponible") else "próximamente"
            md.append(f"- **{g.get('titulo')}** — {g.get('precio', '')} · {estado}")
        if brief.get("aprendizaje"):
            md += ["", "## Aprendizaje activo"]
            for a in brief["aprendizaje"]:
                md.append(f"- {a}")

        path_md = ctx.paths["output"] / "brief.md"
        path_md.write_text("\n".join(md), encoding="utf-8")
        print(f"     catálogo: {len(guias)} guías · {len(roles)} roles")
        return AgentResult(ok=True, artifacts=[str(ctx.paths["brief"]), str(path_md)])

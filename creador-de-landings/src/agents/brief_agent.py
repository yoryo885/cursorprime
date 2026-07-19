"""Arma brief JSON + markdown (catálogo + copy profesional de marketing)."""

from __future__ import annotations

from src.catalog import ensure_catalog, guias_from_catalog, roles_from_catalog, serie_from_catalog
from src.config import save_json
from src.copy_marketing import copy_profesional, enriquecer_productos
from src.learning import aplicar_al_brief
from src.palettes import elegir_paleta
from src.types import AgentResult, PipelineContext


class BriefAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        r = ctx.respuestas
        ejemplo = ctx.ejemplo or r.get("estilo") or r.get("estilo_preferido") or "editorial"
        if ejemplo == "auto":
            ejemplo = "tienda"
        catalog = ensure_catalog(ctx.slug)
        guias = guias_from_catalog(catalog)
        roles = roles_from_catalog(catalog)
        serie = serie_from_catalog(catalog)
        paleta = elegir_paleta(r)
        marca = r.get("marca") or ctx.slug
        precio = r.get("precio") or "desde $4.99"
        copy = copy_profesional(marca, len(guias), len(roles), precio)
        productos = enriquecer_productos(guias, serie)

        # Promesa: preferir copy profesional salvo que el usuario pidió otra explícita no-default
        promesa_user = (r.get("promesa") or "").strip()
        promesa_default_entrevista = "Ideas de libros aplicadas a tu rol — elige tu guía"
        if promesa_user and promesa_user != promesa_default_entrevista:
            promesa = promesa_user
        else:
            promesa = copy["promesa"]

        brief = {
            "marca": marca,
            "producto": r.get("producto") or "Guías PDF profesionales libro × rol",
            "cliente": r.get("cliente") or "Profesionales por oficio",
            "promesa": promesa,
            "cta": r.get("cta") or "Ver colección",
            "precio": precio,
            "tono": r.get("tono") or "editorial",
            "estilo": ejemplo,
            "paleta": paleta,
            "idea": r.get("idea") or "",
            "referencia": r.get("referencia") or "",
            "serie_libros": serie,
            "roles": roles,
            "productos": productos,
            "mostrar_catalogo": True,
            "copy": copy,
            "barra_aviso": copy["barra_aviso"],
            "hero_eyebrow": copy["hero_eyebrow"],
            "hero_titulo": copy["hero_titulo"],
            "hero_sub": copy["hero_sub"],
            "hero_badge_calidad": copy["hero_badge_calidad"],
            "historia": copy["historia"],
            "mision": copy["mision"],
            "beneficios": copy["beneficios"],
            "calidad": copy["calidad"],
            "incluye": copy["incluye"],
            "faq": copy["faq"],
            "newsletter_titulo": copy["newsletter_titulo"],
            "newsletter_sub": copy["newsletter_sub"],
            "newsletter_cta": copy["newsletter_cta"],
            "social_proof_nota": copy["social_proof_nota"],
            "catalogo_titulo": copy["catalogo_titulo"],
            "catalogo_sub": copy["catalogo_sub"],
            "serie_titulo": copy["serie_titulo"],
            "serie_sub": copy["serie_sub"],
            "calidad_titulo": copy["calidad_titulo"],
            "incluye_titulo": copy["incluye_titulo"],
            "testimonios": [
                {"texto": "[PENDIENTE: testimonio real]", "autor": "Cliente"},
            ],
        }
        brief = aplicar_al_brief(brief)
        save_json(ctx.paths["brief"], brief)

        md = [
            f"# Landing brief — {brief['marca']}",
            "",
            f"- **Estilo:** {brief['estilo']}",
            f"- **Paleta:** {paleta.get('nombre')} ({paleta.get('clima')}/{paleta.get('id')})",
            f"- **Promesa:** {brief['promesa']}",
            f"- **CTA:** {brief['cta']}",
            f"- **Productos en catálogo:** {len(productos)}",
            "",
            "## Copy marketing",
            f"- Hero: {brief['hero_titulo']}",
            f"- Calidad: {len(brief['calidad'])} pilares",
            "",
            "## Serie (libros)",
        ]
        for s in serie:
            md.append(f"- {s.get('titulo')} ({s.get('slug')})")
        md += ["", "## Guías (libro × rol)"]
        for g in productos:
            estado = "disponible" if g.get("disponible") else "próximamente"
            md.append(f"- **{g.get('titulo')}** — {g.get('precio', '')} · {estado}")

        path_md = ctx.paths["output"] / "brief.md"
        path_md.write_text("\n".join(md), encoding="utf-8")
        print(f"     catálogo: {len(productos)} guías · {len(roles)} roles · copy profesional")
        return AgentResult(ok=True, artifacts=[str(ctx.paths["brief"]), str(path_md)])

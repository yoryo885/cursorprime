"""Brief unificado de marketing — fuente de verdad para todos los agentes de copy."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.marketing.context_loader import MarketingContext
from src.marketing.pdf_reader import PDFContent
from src.serie import load_serie_config


@dataclass
class MarketingBrief:
    slug: str = ""
    audiencia_oficial: str = ""
    titulo_pdf: str = ""
    portada_aprobada: bool = False
    serie_kdp: str = ""
    marca: str = ""
    libro_fuente: str = ""
    subtitulo_portada: str = ""
    elementos_obligatorios: list[str] = field(default_factory=list)
    lexico_rol: list[str] = field(default_factory=list)
    kpis_rol: list[str] = field(default_factory=list)
    semanas_plan: int = 0
    plantilla_vacia: bool = False
    temas_plan: list[str] = field(default_factory=list)
    reglas_titulo: list[str] = field(default_factory=list)
    prohibiciones: list[str] = field(default_factory=list)
    conflictos: list[str] = field(default_factory=list)
    seed_titulo_kdp: str = ""
    seed_obsoleto: bool = False
    reto_usuario: str = ""
    intro_audiencia: str = ""
    ctx: MarketingContext | None = None

    def to_prompt_block(self) -> str:
        payload: dict[str, Any] = {
            "audiencia_oficial": self.audiencia_oficial,
            "titulo_pdf_aprobado": self.titulo_pdf if self.portada_aprobada else "",
            "portada_aprobada": self.portada_aprobada,
            "serie_solo_kdp": self.serie_kdp,
            "marca": self.marca,
            "libro_fuente": self.libro_fuente,
            "elementos_obligatorios_en_copy": self.elementos_obligatorios,
            "lexico_del_rol": self.lexico_rol[:12],
            "kpis_del_rol": self.kpis_rol[:8],
            "semanas_plan_accion": self.semanas_plan,
            "plantilla_vacia_incluida": self.plantilla_vacia,
            "temas": self.temas_plan[:12],
            "reto_usuario": self.reto_usuario,
            "prohibiciones": self.prohibiciones,
            "reglas_titulo": self.reglas_titulo,
        }
        if self.conflictos:
            payload["conflictos_detectados"] = self.conflictos
        if self.seed_obsoleto:
            payload["nota_borrador"] = (
                "meta/kdp_listing.json está desactualizado vs portada aprobada; "
                "priorizar titulo_pdf_aprobado, no el borrador."
            )
        if self.intro_audiencia:
            payload["intro_audiencia"] = self.intro_audiencia[:1200]
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_constraints_block(self) -> str:
        if not self.reglas_titulo:
            return ""
        lines = "\n".join(f"- {r}" for r in self.reglas_titulo)
        return f"""
REGLAS DE ALINEACIÓN (brief de marketing):
{lines}
"""


def build_marketing_brief(
    ctx: MarketingContext,
    pdf: PDFContent | None = None,
) -> MarketingBrief:
    cfg = load_serie_config()
    seed = ctx.kdp_seed or {}
    serie = str(cfg.get("nombre_serie") or seed.get("serie") or "Aplicar en tu rol")
    marca = str(cfg.get("marca_editorial") or seed.get("marca") or "Libros a Entender")

    libro = str(
        seed.get("libro_fuente")
        or ctx.producto.get("subtitulo_portada")
        or (pdf.titulo_inferido if pdf else "")
        or ""
    ).strip()

    audiencia = ctx.audiencia or str(seed.get("audiencia") or "").strip()
    seed_titulo = str(seed.get("titulo_kdp") or "").strip()
    titulo_pdf = ctx.titulo_pdf

    conflictos: list[str] = []
    seed_obsoleto = False
    if ctx.portada_aprobada and titulo_pdf and seed_titulo:
        if seed_titulo.lower() != titulo_pdf.lower():
            conflictos.append(
                f"Borrador KDP «{seed_titulo}» ≠ portada aprobada «{titulo_pdf}»"
            )
            seed_obsoleto = True
    seed_portada = str(seed.get("titulo_portada_pdf") or "").strip()
    if seed_portada and titulo_pdf and seed_portada.lower() != titulo_pdf.lower():
        conflictos.append(
            f"Seed titulo_portada_pdf «{seed_portada}» ≠ producto «{titulo_pdf}»"
        )
        seed_obsoleto = True

    reglas_titulo: list[str] = []
    if ctx.portada_aprobada and titulo_pdf:
        reglas_titulo.extend([
            f"El título Amazon DEBE reflejar la portada aprobada: «{titulo_pdf}»",
            "Puedes añadir beneficio SEO después de «:» pero NO cambiar la promesa central",
            "Si la portada dice «10 semanas», el título KDP debe incluir «10 semanas»",
            "NO pedir cambiar la portada del PDF ni reemplazar «Resumen personal»",
        ])
    else:
        reglas_titulo.append(
            "Título comercial claro: concepto + rol + beneficio concreto (máx. 200 chars)"
        )

    prohibiciones = [str(p) for p in ctx.rol_perfil.get("prohibido", []) if p]
    prohibiciones.extend([
        "superlativos vacíos (#1, el mejor, gratis)",
        "afirmar afiliación con el autor o editorial original",
    ])

    return MarketingBrief(
        slug=ctx.slug,
        audiencia_oficial=audiencia,
        titulo_pdf=titulo_pdf,
        portada_aprobada=ctx.portada_aprobada,
        serie_kdp=serie,
        marca=marca,
        libro_fuente=libro,
        subtitulo_portada=str(ctx.producto.get("subtitulo_portada") or "").strip(),
        elementos_obligatorios=list(ctx.elementos_producto),
        lexico_rol=list(ctx.lexico_rol),
        kpis_rol=list(ctx.kpis_rol),
        semanas_plan=ctx.semanas_plan,
        plantilla_vacia=ctx.plantilla_vacia,
        temas_plan=list(ctx.temas_plan),
        reglas_titulo=reglas_titulo,
        prohibiciones=prohibiciones,
        conflictos=conflictos,
        seed_titulo_kdp=seed_titulo,
        seed_obsoleto=seed_obsoleto,
        reto_usuario=str(ctx.contexto_usuario.get("reto") or ctx.rol_perfil.get("reto") or ""),
        intro_audiencia=ctx.intro_audiencia,
        ctx=ctx,
    )

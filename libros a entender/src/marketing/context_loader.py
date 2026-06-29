"""Contexto estructurado de producción para agentes de marketing (solo lectura)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


@dataclass
class MarketingContext:
    slug: str = ""
    contexto_usuario: dict[str, Any] = field(default_factory=dict)
    producto: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    plan_accion: dict[str, Any] = field(default_factory=dict)
    rol_perfil: dict[str, Any] = field(default_factory=dict)
    kdp_seed: dict[str, Any] = field(default_factory=dict)
    intro_audiencia: str = ""
    temas_plan: list[str] = field(default_factory=list)
    semanas_plan: int = 0
    plantilla_vacia: bool = False
    lexico_rol: list[str] = field(default_factory=list)
    kpis_rol: list[str] = field(default_factory=list)
    elementos_producto: list[str] = field(default_factory=list)
    titulo_pdf: str = ""
    portada_aprobada: bool = False

    @property
    def audiencia(self) -> str:
        return str(
            self.contexto_usuario.get("audiencia")
            or self.contexto_usuario.get("ocupacion")
            or self.kdp_seed.get("audiencia")
            or ""
        ).strip()

    def to_prompt_block(self) -> str:
        import json as _json

        payload = {
            "audiencia": self.audiencia,
            "titulo_pdf_aprobado": self.titulo_pdf if self.portada_aprobada else "",
            "portada_aprobada": self.portada_aprobada,
            "temas": self.temas_plan[:12],
            "semanas_plan_accion": self.semanas_plan,
            "plantilla_vacia_incluida": self.plantilla_vacia,
            "elementos_que_incluye_el_pdf": self.elementos_producto,
            "lexico_del_rol": self.lexico_rol[:12],
            "kpis_del_rol": self.kpis_rol[:8],
            "reto_usuario": self.contexto_usuario.get("reto", ""),
            "propuesta_producto": self.producto.get("titulo_comercial", ""),
            "checklist": self.producto.get("checklist_titulo", ""),
        }
        if self.intro_audiencia:
            payload["intro_audiencia"] = self.intro_audiencia[:1200]
        return _json.dumps(payload, ensure_ascii=False, indent=2)


def load_marketing_context(pdf_path: Path) -> MarketingContext:
    """Carga meta/ de producción junto al PDF — marketing no escribe aquí."""
    pdf_path = Path(pdf_path)
    slug_dir = pdf_path.parent
    meta = slug_dir / "meta"
    ctx = MarketingContext(slug=slug_dir.name)

    ctx.contexto_usuario = _read_json(slug_dir / "contexto_usuario.json")
    ctx.producto = _read_json(meta / "producto.json")
    ctx.plan = _read_json(meta / "plan.json")
    ctx.plan_accion = _read_json(meta / "plan_accion.json")
    ctx.rol_perfil = _read_json(meta / "rol_perfil.json")
    ctx.kdp_seed = _read_json(meta / "kdp_listing.json")
    ctx.intro_audiencia = _read_text(meta / "intro_audiencia.txt")

    ctx.temas_plan = [
        str(t.get("nombre") or t.get("tema") or "")
        for t in ctx.plan.get("temas", [])
        if isinstance(t, dict)
    ]
    ctx.temas_plan = [t for t in ctx.temas_plan if t]

    filas = ctx.plan_accion.get("filas") or []
    ctx.semanas_plan = len(filas) if isinstance(filas, list) else 0
    ctx.plantilla_vacia = bool(ctx.plan_accion.get("incluir_plantilla_vacia"))

    ctx.lexico_rol = [str(x) for x in ctx.rol_perfil.get("lexico", []) if x][:15]
    ctx.kpis_rol = [str(x) for x in ctx.rol_perfil.get("kpis", []) if x][:10]

    ctx.titulo_pdf = str(ctx.producto.get("titulo_comercial") or "").strip()
    ctx.portada_aprobada = bool(ctx.producto.get("portada_aprobada"))

    ctx.elementos_producto = [
        "Resúmenes por tema adaptados al rol",
        "Mapa conceptual",
        "Tarjetas: idea clave, ejemplo y aplicación",
    ]
    if ctx.semanas_plan:
        ctx.elementos_producto.append(
            f"Plan de acción de {ctx.semanas_plan} semanas con acciones concretas"
        )
    if ctx.plantilla_vacia:
        ctx.elementos_producto.append(
            "Plantilla en blanco para escribir tu propio plan semanal"
        )
    if ctx.producto.get("checklist_items"):
        ctx.elementos_producto.append(
            f"Checklist imprimible: {ctx.producto.get('checklist_titulo', 'seguimiento semanal')}"
        )
    if ctx.producto.get("mini_guia"):
        ctx.elementos_producto.append("Mini guía de inicio")

    return ctx

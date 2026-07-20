"""01 — Brief: normaliza input del negocio → brief.json"""

from __future__ import annotations

from typing import Any


def run(input: dict[str, Any]) -> dict[str, Any]:
    """
    input: producto, rubro, precio, publico, tono, marca?, slug?, extras?
    → brief estructurado con nombre_producto + propuesta_valor (fuente de verdad pública)
    """
    marca = (input.get("marca") or input.get("nombre_producto") or input.get("producto") or "Marca").strip()
    # nombre público: NO usar slugs/datasets internos
    nombre_producto = (
        input.get("nombre_producto") or marca or input.get("producto") or "Producto"
    ).strip()
    # producto interno (catálogo) — no debe filtrarse al copy público
    producto_interno = (input.get("producto") or "").strip()
    rubro = (input.get("rubro") or "general").strip()
    precio = (input.get("precio") or "").strip()
    publico = (input.get("publico") or input.get("público") or "profesionales").strip()
    tono = (input.get("tono") or "claro y profesional").strip()
    slug = (input.get("slug") or _slugify(nombre_producto)).strip()
    propuesta_valor = (
        input.get("propuesta_valor") or input.get("promesa") or ""
    ).strip()
    if not propuesta_valor:
        propuesta_valor = f"{nombre_producto} para {publico}"

    brief = {
        "slug": slug,
        "marca": marca,
        "nombre_producto": nombre_producto,
        "propuesta_valor": propuesta_valor,
        "producto": producto_interno or nombre_producto,  # legacy; agentes deben preferir nombre_producto
        "producto_interno": producto_interno,
        "rubro": rubro,
        "precio": precio,
        "publico": publico,
        "tono": tono,
        "promesa": propuesta_valor,
        "cta": (input.get("cta") or "Ver más").strip(),
        "contacto": (input.get("contacto") or "").strip(),
        "n_productos": int(input.get("n_productos") or 1),
        "n_roles": int(input.get("n_roles") or 1),
        "testimonios": input.get("testimonios") or (input.get("extras") or {}).get("testimonios") or [],
        "extras": input.get("extras") or {},
    }
    return brief


def _slugify(s: str) -> str:
    out = []
    for ch in s.lower().strip():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "landing"

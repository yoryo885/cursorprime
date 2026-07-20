"""01 — Brief: normaliza input del negocio → brief.json"""

from __future__ import annotations

from typing import Any


def run(input: dict[str, Any]) -> dict[str, Any]:
    """
    input: producto, rubro, precio, publico, tono, marca?, slug?, extras?
    → brief estructurado
    """
    marca = (input.get("marca") or input.get("producto") or "Marca").strip()
    producto = (input.get("producto") or marca).strip()
    rubro = (input.get("rubro") or "general").strip()
    precio = (input.get("precio") or "").strip()
    publico = (input.get("publico") or input.get("público") or "profesionales").strip()
    tono = (input.get("tono") or "claro y profesional").strip()
    slug = (input.get("slug") or _slugify(marca)).strip()

    brief = {
        "slug": slug,
        "marca": marca,
        "producto": producto,
        "rubro": rubro,
        "precio": precio,
        "publico": publico,
        "tono": tono,
        "promesa": (input.get("promesa") or "").strip(),
        "cta": (input.get("cta") or "Ver más").strip(),
        "contacto": (input.get("contacto") or "").strip(),
        "n_productos": int(input.get("n_productos") or 1),
        "n_roles": int(input.get("n_roles") or 1),
        "extras": input.get("extras") or {},
    }
    if not brief["promesa"]:
        brief["promesa"] = f"{producto} para {publico}"
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

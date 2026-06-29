"""Aplicar mejoras propuestas a weights.json — V2."""

from __future__ import annotations

from src.config import load_json, save_json, weights_path


def aplicar_mejoras(meta_dir, confirm: bool = False) -> list[str]:
    prop = load_json(meta_dir / "mejoras_propuestas.json", {})
    propuestas = prop.get("propuestas", [])
    if not propuestas:
        return ["Sin propuestas"]
    if not confirm:
        return ["Usa --aplicar-mejoras con confirmación explícita en CLI"]

    weights = load_json(weights_path(), {})
    applied = []
    for p in propuestas:
        if p.get("tipo") == "pesos" and p.get("campo"):
            for tipo in weights.get("tipos", {}):
                w = weights["tipos"][tipo]
                if p["campo"] in w:
                    w[p["campo"]] = max(0.05, min(0.4, w[p["campo"]] + p.get("delta", 0)))
                    applied.append(f"{tipo}.{p['campo']} ajustado")
    save_json(weights_path(), weights)
    return applied or ["Nada aplicable automáticamente"]

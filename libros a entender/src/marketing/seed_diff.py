"""Compara listing generado vs borrador meta/kdp_listing.json."""
from __future__ import annotations

from typing import Any


def compute_diff_vs_seed(
    *,
    titulo: str,
    subtitulo: str,
    keywords: list[str],
    seed: dict[str, Any],
) -> dict[str, str]:
    diff: dict[str, str] = {}
    seed_titulo = str(seed.get("titulo_kdp") or "").strip()
    if seed_titulo and seed_titulo.lower() != (titulo or "").strip().lower():
        diff["titulo"] = f"borrador: «{seed_titulo}» → generado: «{titulo}»"

    seed_sub = str(seed.get("subtitulo_kdp") or "").strip()
    if seed_sub and seed_sub.lower() != (subtitulo or "").strip().lower():
        diff["subtitulo"] = f"borrador: «{seed_sub}» → generado: «{subtitulo}»"

    seed_kws = [str(k).strip().lower() for k in seed.get("keywords", []) if k]
    gen_kws = [k.strip().lower() for k in keywords if k.strip()]
    if seed_kws:
        nuevas = [k for k in gen_kws if k not in seed_kws]
        perdidas = [k for k in seed_kws if k not in gen_kws]
        if nuevas or perdidas:
            parts = []
            if perdidas:
                parts.append(f"quitadas: {', '.join(perdidas[:3])}")
            if nuevas:
                parts.append(f"nuevas: {', '.join(nuevas[:3])}")
            diff["keywords"] = "; ".join(parts)

    return diff

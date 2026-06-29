"""Comparar dos ideas analizadas — V2."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json, slug_meta, slug_output


def compare(slug_a: str, slug_b: str) -> dict:
    va = load_json(slug_meta(slug_a) / "verdict.json", {})
    vb = load_json(slug_meta(slug_b) / "verdict.json", {})
    if not va or not vb:
        raise SystemExit(f"Faltan análisis para {slug_a} y/o {slug_b}. Corre pipeline primero.")

    areas_a = va.get("por_area", {})
    areas_b = vb.get("por_area", {})
    all_areas = set(areas_a) | set(areas_b)
    lado_a = {}
    lado_b = {}
    ganador = {}

    for area in all_areas:
        sa = areas_a.get(area, {}).get("score", 0)
        sb = areas_b.get(area, {}).get("score", 0)
        lado_a[area] = sa
        lado_b[area] = sb
        if sa > sb:
            ganador[area] = slug_a
        elif sb > sa:
            ganador[area] = slug_b
        else:
            ganador[area] = "empate"

    pa = va.get("score_global", {}).get("point", 0)
    pb = vb.get("score_global", {}).get("point", 0)
    winner = slug_a if pa >= pb else slug_b

    result = {
        "slug_a": slug_a,
        "slug_b": slug_b,
        "score_a": pa,
        "score_b": pb,
        "veredicto_a": va.get("veredicto"),
        "veredicto_b": vb.get("veredicto"),
        "por_area_a": lado_a,
        "por_area_b": lado_b,
        "ganador_por_area": ganador,
        "ganador_global": winner,
        "trade_offs": [f"{slug_a} mejor en {k}" for k, v in ganador.items() if v == slug_a],
        "generado_at": datetime.now(timezone.utc).isoformat(),
    }

    out_dir = slug_output(slug_a).parent.parent / "_compare"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"compare_{slug_a}_{slug_b}.json"
    save_json(out_path, result)
    return result

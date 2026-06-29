"""Escaneo enriquecido de analisis-de-proyectos para el panel."""

from __future__ import annotations

from pathlib import Path

from src.config import CURSORPRIME, load_json


def scan_analisis_detalle() -> tuple[list[dict], dict | None]:
    root = CURSORPRIME / "analisis-de-proyectos"
    data_root = root / "data"
    ideas_root = CURSORPRIME / "ideas de proyectos"

    # idea exportada → analisis_slug
    idea_por_analisis: dict[str, dict] = {}
    for p in (ideas_root / "ideas" / "from-analisis").glob("*.json"):
        d = load_json(p, {}) or {}
        slug_a = d.get("analisis_slug")
        if slug_a:
            idea_por_analisis[slug_a] = {"idea_slug": d.get("slug"), "titulo": d.get("titulo")}

    # evaluación por slug de idea
    eval_por_idea: dict[str, dict] = {}
    for p in (ideas_root / "evaluaciones").glob("*/veredicto.json"):
        d = load_json(p, {}) or {}
        eval_por_idea[p.parent.name] = {
            "veredicto": d.get("veredicto"),
            "score": d.get("score"),
            "confidence": d.get("confidence"),
            "margen": d.get("margen"),
            "siguiente_paso": d.get("siguiente_paso"),
        }

    items: list[dict] = []
    for d in sorted(data_root.iterdir()) if data_root.exists() else []:
        if not d.is_dir() or d.name.startswith("."):
            continue
        meta_path = d / "meta" / "analisis.json"
        fetch_path = d / "meta" / "fetch.json"
        if not meta_path.exists() and not fetch_path.exists():
            continue

        meta = load_json(meta_path, {}) or {}
        fetch = load_json(fetch_path, {}) or {}
        slug = d.name

        idea = idea_por_analisis.get(slug, {})
        ev = eval_por_idea.get(idea.get("idea_slug", ""), {})

        items.append(
            {
                "slug": slug,
                "tema": meta.get("tema") or slug,
                "tipo": meta.get("tipo") or ("radar_semanal" if slug.startswith("radar-") else "investigacion"),
                "fetch": "live" if fetch.get("mode") == "live" or fetch.get("mock") is False else "mock",
                "fuentes": fetch.get("total") or len(fetch.get("youtube") or []) + len(fetch.get("web") or []),
                "fecha": (fetch.get("fetched_at") or meta.get("generado_at") or "")[:10],
                "resumen": (meta.get("resumen_ejecutivo") or "")[:120],
                "oportunidades": len(meta.get("oportunidades_pipeline") or []),
                "idea_slug": idea.get("idea_slug") or "—",
                "veredicto": ev.get("veredicto") or "—",
                "score": ev.get("score") if ev.get("score") is not None else "—",
                "informe": f"analisis-de-proyectos/data/{slug}/output/analisis.md",
            }
        )

    items.sort(key=lambda x: x.get("fecha") or "", reverse=True)

    radar_state = load_json(root / "meta" / "radar_auto_state.json", {}) or {}
    ultimo = items[0] if items else None
    if ultimo and radar_state.get("ultima_corrida", {}).get("slug") == ultimo["slug"]:
        ultimo = {**ultimo, "radar_auto": radar_state.get("ultima_corrida")}

    return items, ultimo

"""Exporta análisis → borrador de idea en ideas de proyectos."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import IDEAS_FROM_ANALISIS, analisis_path, load_json, save_json, slugify


def analisis_a_idea(analisis: dict, analisis_slug: str) -> dict:
    tema = analisis.get("tema") or analisis_slug
    oportunidades = analisis.get("oportunidades_pipeline") or []
    primera = oportunidades[0] if oportunidades else {}

    titulo = primera.get("titulo") or f"Proyecto desde análisis: {tema}"
    slug = slugify(titulo)

    return {
        "titulo": titulo,
        "slug": slug,
        "tipo": "from_analisis",
        "analisis_slug": analisis_slug,
        "problema": analisis.get("resumen_ejecutivo") or "",
        "cliente_objetivo": "Emprendedor / creador de productos digitales",
        "modelo_negocio": "Pipeline automatizado → producto o venta del sistema",
        "hipotesis": [
            op.get("razon") or op.get("titulo")
            for op in oportunidades[:3]
        ] or ["Validar demanda con MVP mínimo"],
        "productos_que_funcionan": analisis.get("productos_que_funcionan") or [],
        "patrones": analisis.get("patrones") or [],
        "fuentes_count": len(analisis.get("fuentes") or []),
        "confidence_analisis": primera.get("confidence"),
        "exportado_at": datetime.now(timezone.utc).isoformat(),
        "notas": f"Generado desde analisis-de-proyectos/data/{analisis_slug}/",
        "siguiente_paso": "python3 evaluar.py ideas/from-analisis/{slug}.json",
    }


def exportar_a_proyectos(analisis_slug: str) -> dict:
    path = analisis_path(analisis_slug)
    if not path.exists():
        return {"ok": False, "error": f"No hay análisis: {path}"}

    analisis = load_json(path, {}) or {}
    idea = analisis_a_idea(analisis, analisis_slug)
    IDEAS_FROM_ANALISIS.mkdir(parents=True, exist_ok=True)
    out = IDEAS_FROM_ANALISIS / f"{idea['slug']}.json"
    save_json(out, idea)
    return {"ok": True, "path": str(out), "slug": idea["slug"], "idea": idea}


def listar_analisis() -> list[dict]:
    from src.config import DATA_DIR

    out = []
    if not DATA_DIR.exists():
        return out
    for d in sorted(DATA_DIR.iterdir()):
        if not d.is_dir():
            continue
        ap = d / "meta" / "analisis.json"
        if ap.exists():
            data = load_json(ap, {}) or {}
            out.append({"slug": d.name, "tema": data.get("tema"), "path": str(ap)})
    return out

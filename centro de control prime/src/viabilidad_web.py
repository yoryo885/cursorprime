"""Viabilidad por proyecto — fetch YouTube + web (mismo motor que analisis-de-proyectos)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import CURSORPRIME, META_DIR, load_json, save_json
from src.modulos import CAPA_CREADOR, CAPA_PRODUCTO, MODULO_SECCIONES, modulos_estado

VIAB_DIR = META_DIR / "viabilidad"
ANALISIS_ROOT = CURSORPRIME / "analisis-de-proyectos"

TEMAS: dict[str, str] = {
    "router": "cursor ai agent skills automation workflow developer",
    "analisis": "market research pipeline digital product kdp youtube automation",
    "lluvia": "brainstorm product ideas digital business automation 2026",
    "ideas": "startup idea evaluation viability side project saas",
    "project_lens": "business viability market analysis tool entrepreneur",
    "prompts": "ai prompt templates automation cursor pipeline",
    "skills": "cursor agent custom skills workflow automation",
    "panel": "project dashboard control panel productivity software",
    "marketing_audit": "local business marketing audit digital presence 2026",
    "clientes": "digital agency client onboarding local business",
    "embudo": "sales funnel local business marketing audit proposal",
    "wasap": "whatsapp bot small business latin america automation",
    "presencia": "local business google business profile website seo",
    "contenido": "ai content creation youtube faceless video automation",
    "libros": "amazon kdp book summary niche youtube faceless",
    "linkedin": "linkedin ghostwriter b2b content automation posts",
}


def _fetch_live(queries: list[str]) -> tuple[list[dict], list[dict], list[str]]:
    import json
    import subprocess

    code = """
import json, sys
sys.path.insert(0, sys.argv[1])
from src.agents.fetch_agent import fetch_live
queries = json.loads(sys.argv[2])
yt, web, w = fetch_live(queries)
print(json.dumps({"youtube": yt, "web": web, "warnings": w}, ensure_ascii=False))
"""
    r = subprocess.run(
        [sys.executable, "-c", code, str(ANALISIS_ROOT), json.dumps(queries)],
        capture_output=True,
        text=True,
        cwd=str(ANALISIS_ROOT),
    )
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "fetch falló").strip())
    data = json.loads(r.stdout)
    return data.get("youtube") or [], data.get("web") or [], data.get("warnings") or []


def _score(tema: str, youtube: list[dict], web: list[dict]) -> dict:
    total = len(youtube) + len(web)
    text = " ".join(
        (it.get("titulo") or "") + " " + (it.get("snippet") or "")
        for it in youtube + web
    ).lower()

    score = 45
    if total >= 10:
        score += 25
    elif total >= 6:
        score += 18
    elif total >= 3:
        score += 10
    if youtube and web:
        score += 8
    signals = (
        "kdp", "amazon", "pipeline", "automation", "saas", "youtube",
        "profitable", "business", "niche", "faceless", "digital product",
    )
    score += min(17, sum(2 for s in signals if s in text))
    score = min(100, max(20, score))

    if score >= 72:
        veredicto = "viable"
    elif score >= 52:
        veredicto = "condicional"
    else:
        veredicto = "descartar"

    oportunidades = 0
    if total >= 8:
        oportunidades = 2
    elif total >= 4:
        oportunidades = 1

    resumen = f"Investigación sobre «{tema}»: {len(youtube)} YouTube · {len(web)} web. "
    if veredicto == "viable":
        resumen += "Hay señales de demanda y productos similares activos hoy."
    elif veredicto == "condicional":
        resumen += "Demanda parcial — conviene nicho más específico o MVP pequeño."
    else:
        resumen += "Poca señal en fuentes — revisar tema o profundizar búsqueda."

    confidence = round(min(0.85, 0.25 + total * 0.04), 2)

    return {
        "veredicto": veredicto,
        "score": score,
        "oportunidades": oportunidades,
        "resumen_ejecutivo": resumen,
        "confidence": confidence,
    }


def _write_informe(path: Path, data: dict) -> None:
    lines = [
        f"# Viabilidad — {data.get('nombre', data.get('id'))}",
        "",
        f"**Tema:** {data.get('tema')}",
        f"**Veredicto:** {data.get('veredicto')} ({data.get('score')}/100)",
        f"**Fuentes:** {data.get('fuentes')} ({data.get('fetch', 'live')})",
        f"**Fecha:** {(data.get('fecha') or '')[:10]}",
        "",
        data.get("resumen", ""),
        "",
        "## YouTube",
    ]
    for it in data.get("youtube") or []:
        lines.append(f"- [{it.get('titulo', '')[:80]}]({it.get('url', '')})")
    lines.append("")
    lines.append("## Web")
    for it in data.get("web") or []:
        lines.append(f"- [{it.get('titulo', '')[:80]}]({it.get('url', '')})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def investigar_proyecto(mod: dict, *, live: bool = True) -> dict:
    pid = mod["id"]
    tema = TEMAS.get(pid, mod.get("nombre", pid))
    queries = [tema]

    if live:
        youtube, web, warnings = _fetch_live(queries)
        mode = "live"
    else:
        youtube, web, warnings = [], [], ["mock — usa --live"]
        mode = "mock"

    scored = _score(tema, youtube, web)
    now = datetime.now(timezone.utc).isoformat()
    slug = f"viabilidad-{pid}"

    data = {
        "id": pid,
        "slug": slug,
        "nombre": mod.get("nombre"),
        "carpeta": mod.get("carpeta"),
        "capa": mod.get("capa"),
        "tema": tema,
        "fetch": mode,
        "fuentes": len(youtube) + len(web),
        "youtube_n": len(youtube),
        "web_n": len(web),
        "fecha": now[:10],
        "generado_at": now,
        "veredicto": scored["veredicto"],
        "score": scored["score"],
        "oportunidades": scored["oportunidades"],
        "resumen": scored["resumen_ejecutivo"],
        "confidence": scored["confidence"],
        "warnings": warnings,
        "youtube": youtube[:6],
        "web": web[:6],
        "informe": f"centro de control prime/meta/viabilidad/{pid}.md",
    }

    VIAB_DIR.mkdir(parents=True, exist_ok=True)
    save_json(VIAB_DIR / f"{pid}.json", data)
    _write_informe(VIAB_DIR / f"{pid}.md", data)
    return data


def investigar_todos(
    *,
    live: bool = True,
    capa: str | None = None,
    limit: int | None = None,
    force: bool = False,
) -> list[dict]:
    mods = modulos_estado()
    if capa:
        mods = [m for m in mods if m.get("capa") == capa]
    if limit:
        mods = mods[:limit]

    out: list[dict] = []
    for i, m in enumerate(mods, 1):
        cache = VIAB_DIR / f"{m['id']}.json"
        if not force and cache.exists() and live:
            cached = load_json(cache, {}) or {}
            if cached.get("fetch") == "live" and cached.get("fuentes", 0) > 0:
                print(f"  ⏭ {m['nombre']} (cache)")
                out.append(cached)
                continue
        print(f"  [{i}/{len(mods)}] {m['nombre']}…")
        out.append(investigar_proyecto(m, live=live))

    save_json(
        VIAB_DIR / "_index.json",
        {"generado_at": datetime.now(timezone.utc).isoformat(), "items": out},
    )
    return out


def load_viabilidad_cache() -> list[dict]:
    items: list[dict] = []
    if not VIAB_DIR.exists():
        return items
    for p in sorted(VIAB_DIR.glob("*.json")):
        if p.name.startswith("_"):
            continue
        d = load_json(p, {}) or {}
        if d.get("id"):
            items.append(d)
    return items


def viabilidad_por_capas(items: list[dict]) -> dict:
    def _capa(capa_id: str) -> dict:
        info = MODULO_SECCIONES[capa_id]
        proys = [x for x in items if x.get("capa") == capa_id]
        viables = sum(1 for x in proys if x.get("veredicto") == "viable")
        cond = sum(1 for x in proys if x.get("veredicto") == "condicional")
        avg = round(sum(x.get("score", 0) for x in proys) / len(proys)) if proys else 0
        return {
            "id": capa_id,
            "titulo": info["titulo"],
            "subtitulo": info["subtitulo"],
            "total": len(proys),
            "viables": viables,
            "condicionales": cond,
            "score_promedio": avg,
            "proyectos": proys,
        }

    return {
        "generado_at": datetime.now(timezone.utc).isoformat(),
        "total": len(items),
        "capas": [_capa(CAPA_CREADOR), _capa(CAPA_PRODUCTO)],
        "creador": _capa(CAPA_CREADOR),
        "productos": _capa(CAPA_PRODUCTO),
        "items": items,
    }

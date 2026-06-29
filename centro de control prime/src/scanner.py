"""Escanea cursorprime y arma inventario completo."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.analisis_ecosistema import analisis_ecosistema
from src.rentabilidad import load_rentabilidad
from src.viabilidad_web import load_viabilidad_cache, viabilidad_por_capas
from src.analisis_scan import scan_analisis_detalle
from src.config import CURSORPRIME, PROYECTOS, SKILLS_USER, load_json
from src.modulos import clientes_scan, embudo_comercial, modulos_estado, scan_carpetas


_RESERVED = frozenset({"inputs", "meta", "output", "logs", "cola", "cache"})


def _slug_dirs(data_root: Path) -> list[dict]:
    if not data_root.exists():
        return []
    out = []
    for d in sorted(data_root.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in _RESERVED:
            continue
        analisis_meta = d / "meta" / "analisis.json"
        analisis_out = d / "output" / "analisis.json"
        manifest = d / "output" / "manifest.json"
        brief = d / "inputs" / "brief.json"
        if not any(p.exists() for p in (analisis_meta, analisis_out, manifest, brief)):
            continue
        meta = {}
        if analisis_meta.exists():
            meta = load_json(analisis_meta, {}) or {}
        elif analisis_out.exists():
            meta = load_json(analisis_out, {}) or {}
        elif manifest.exists():
            meta = load_json(manifest, {}) or {}
        out.append(
            {
                "slug": d.name,
                "tema": meta.get("tema") or meta.get("titulo") or d.name,
                "tipo": meta.get("tipo") or "lote",
            }
        )
    return out


def _json_files(folder: Path, pattern: str = "*.json") -> list[dict]:
    if not folder.exists():
        return []
    items = []
    for p in sorted(folder.rglob(pattern)):
        if p.name.startswith("."):
            continue
        data = load_json(p, {}) or {}
        items.append(
            {
                "archivo": p.name,
                "path": str(p.relative_to(CURSORPRIME)) if p.is_relative_to(CURSORPRIME) else str(p),
                "slug": p.parent.name,
                "titulo": data.get("titulo") or data.get("slug") or p.stem,
                "estado": data.get("estado") or data.get("veredicto"),
                "score": data.get("score"),
            }
        )
    return items


def _cola_lluvia() -> dict:
    cola_root = PROYECTOS["lluvia-de-ideas"] / "cola"
    counts = {}
    items: dict[str, list] = {}
    for estado in ("pendientes", "aprobadas", "implementadas", "en_espera", "rechazadas"):
        folder = cola_root / estado if estado != "implementadas" else cola_root / "aprobadas"
        if estado == "implementadas":
            all_a = list((cola_root / "aprobadas").glob("idea-*.json")) if (cola_root / "aprobadas").exists() else []
            filtered = []
            for p in all_a:
                if p.name == "prioridad.json":
                    continue
                d = load_json(p, {}) or {}
                if d.get("estado") == "implementada":
                    filtered.append({"id": d.get("id"), "titulo": d.get("titulo"), "categoria": d.get("categoria")})
            items[estado] = filtered
            counts[estado] = len(filtered)
        else:
            folder = cola_root / {"pendientes": "pendientes", "aprobadas": "aprobadas", "en_espera": "en_espera", "rechazadas": "rechazadas"}[estado]
            if estado == "aprobadas":
                raw = []
                for p in (folder.glob("idea-*.json") if folder.exists() else []):
                    if p.name == "prioridad.json":
                        continue
                    d = load_json(p, {}) or {}
                    if d.get("estado") != "implementada":
                        raw.append({"id": d.get("id"), "titulo": d.get("titulo"), "categoria": d.get("categoria")})
                items[estado] = raw
                counts[estado] = len(raw)
            else:
                raw = []
                for p in (folder.glob("idea-*.json") if folder.exists() else []):
                    d = load_json(p, {}) or {}
                    raw.append({"id": d.get("id"), "titulo": d.get("titulo"), "categoria": d.get("categoria")})
                items[estado] = raw
                counts[estado] = len(raw)
    return {"counts": counts, "items": items}


def scan() -> dict:
    analisis_root = PROYECTOS["analisis-de-proyectos"] / "data"
    analisis = _slug_dirs(analisis_root)
    analisis_detalle, analisis_ultimo = scan_analisis_detalle()
    radar_state = load_json(PROYECTOS["analisis-de-proyectos"] / "meta" / "radar_auto_state.json", {}) or {}
    radar_log = load_json(PROYECTOS["analisis-de-proyectos"] / "logs" / "radar_historial.json", []) or []

    ideas_root = PROYECTOS["ideas-de-proyectos"]
    evaluaciones = _json_files(ideas_root / "evaluaciones", "veredicto.json")
    borradores = [d.name for d in (ideas_root / "borradores").iterdir() if d.is_dir()] if (ideas_root / "borradores").exists() else []
    from_analisis = _json_files(ideas_root / "ideas" / "from-analisis")
    from_lluvia = _json_files(ideas_root / "ideas" / "from-lluvia")
    ideas_all = _json_files(ideas_root / "ideas")
    ideas_sueltas = [i for i in ideas_all if "from-analisis" not in i["path"] and "from-lluvia" not in i["path"]]

    contenido = _slug_dirs(PROYECTOS["creador-de-contenido"] / "data")
    prompts = _slug_dirs(PROYECTOS["creador-de-prompts"] / "data")
    skills_data = _slug_dirs(PROYECTOS["creador-de-skills"] / "data")

    skills_instaladas = []
    if SKILLS_USER.exists():
        for p in sorted(SKILLS_USER.iterdir()):
            if p.is_dir() and (p / "SKILL.md").exists():
                skills_instaladas.append(p.name)

    cola = _cola_lluvia()

    proyectos_en_disco = [
        name for name, path in PROYECTOS.items() if path.exists() and (path / "PROYECTO.md").exists()
    ]
    # Proyectos extra con PROYECTO.md o CLI fuera del mapa base
    for extra in ("marketing-audit", "centro de control prime", "libros a entender", "linkedin-ghostwriter", "proyectos-top3"):
        ep = CURSORPRIME / extra
        if ep.exists() and extra.replace("-", "_") not in proyectos_en_disco and extra not in proyectos_en_disco:
            if (ep / "PROYECTO.md").exists() or list(ep.glob("*_main.py")):
                proyectos_en_disco.append(extra)

    modulos = modulos_estado()
    carpetas = scan_carpetas()
    embudo = embudo_comercial()
    clientes = clientes_scan()
    modulos_resumen = {
        "hecho": sum(1 for m in modulos if m["estado"] == "hecho"),
        "parcial": sum(1 for m in modulos if m["estado"] == "parcial"),
        "falta": sum(1 for m in modulos if m["estado"] == "falta"),
    }

    resumen = {
        "analisis": len(analisis),
        "radar_corridas": len(radar_log),
        "cola_pendientes": cola["counts"].get("pendientes", 0),
        "cola_aprobadas": cola["counts"].get("aprobadas", 0),
        "cola_implementadas": cola["counts"].get("implementadas", 0),
        "cola_en_espera": cola["counts"].get("en_espera", 0),
        "evaluaciones": len(evaluaciones),
        "borradores": len(borradores),
        "ideas_from_analisis": len(from_analisis),
        "ideas_from_lluvia": len(from_lluvia),
        "packs_contenido": len(contenido),
        "lotes_prompts": len(prompts),
        "skills_generadas": len(skills_data),
        "skills_instaladas": len(skills_instaladas),
        "proyectos_activos": len(proyectos_en_disco),
        "carpetas_total": len(carpetas),
        "modulos_hecho": modulos_resumen["hecho"],
        "modulos_parcial": modulos_resumen["parcial"],
        "clientes_total": len(clientes),
        "analisis_live": sum(1 for a in analisis_detalle if a.get("fetch") == "live"),
        "radar_semana_ok": radar_state.get("ultima_semana_ok"),
    }

    eco = analisis_ecosistema(modulos, resumen)
    viab_items = load_viabilidad_cache()
    viabilidad = viabilidad_por_capas(viab_items)

    return {
        "version": 1,
        "nombre": "Centro de control prime",
        "generado_at": datetime.now(timezone.utc).isoformat(),
        "resumen": resumen,
        "proyectos": proyectos_en_disco,
        "analisis": analisis,
        "analisis_detalle": analisis_detalle,
        "analisis_ultimo": analisis_ultimo,
        "radar_auto": radar_state,
        "radar_historial": radar_log[-8:],
        "cola_lluvia": cola,
        "evaluaciones": evaluaciones,
        "borradores": borradores,
        "ideas_from_analisis": from_analisis,
        "ideas_from_lluvia": from_lluvia,
        "ideas": ideas_sueltas,
        "contenido": contenido,
        "prompts": prompts,
        "skills_generadas": skills_data,
        "skills_instaladas": skills_instaladas,
        "flujo": [
            {"paso": 1, "nombre": "Análisis", "proyecto": "analisis-de-proyectos", "count": resumen["analisis"]},
            {"paso": 2, "nombre": "Lluvia + OK", "proyecto": "lluvia-de-ideas", "count": sum(cola["counts"].values())},
            {"paso": 3, "nombre": "Evaluar / diseñar", "proyecto": "ideas-de-proyectos", "count": resumen["evaluaciones"] + resumen["borradores"]},
            {"paso": 4, "nombre": "Producir assets", "proyecto": "creador-de-contenido", "count": resumen["packs_contenido"]},
        ],
        "carpetas": carpetas,
        "modulos": modulos,
        "modulos_resumen": modulos_resumen,
        "analisis_ecosistema": eco,
        "viabilidad_proyectos": viabilidad,
        "embudo_comercial": embudo,
        "embudo_index": "clientes/clinica-sol/proyectos/audit-inicial/entregables/index.html",
        "rentabilidad": load_rentabilidad(),
        "clientes": clientes,
    }

"""Análisis agregado del ecosistema cursorprime — creador vs proyectos creados."""

from __future__ import annotations

from datetime import datetime, timezone

from src.modulos import CAPA_CREADOR, CAPA_PRODUCTO, MODULO_SECCIONES


def _diagnostico_modulo(m: dict) -> tuple[str, str]:
    estado = m.get("estado", "parcial")
    pct = int(m.get("avance_pct") or 0)
    pend = m.get("pendientes") or []

    if estado == "hecho":
        return "Operativo. Sin pendientes críticos.", "baja"
    if estado == "falta":
        return "Por iniciar o sin avance en disco.", "alta"
    if not pend:
        return f"Avance {pct}%. Sin tareas listadas.", "baja"
    if len(pend) == 1:
        return f"Demo funcional. Falta: {pend[0]}.", "media"
    if len(pend) >= 3:
        return f"Avance {pct}%. {len(pend)} tareas abiertas.", "alta"
    return f"Avance {pct}%. Pendiente: {' · '.join(pend[:2])}.", "media"


def _veredicto_capa(hecho: int, parcial: int, falta: int, total: int) -> str:
    if total == 0:
        return "sin datos"
    if hecho == total:
        return "maduro"
    if hecho + parcial >= total * 0.75:
        return "avanzado"
    if parcial >= total * 0.4:
        return "en construcción"
    return "temprano"


def _analizar_capa(modulos: list[dict], capa_id: str) -> dict:
    info = MODULO_SECCIONES[capa_id]
    proyectos: list[dict] = []

    for m in modulos:
        diag, prioridad = _diagnostico_modulo(m)
        proyectos.append(
            {
                "id": m.get("id"),
                "nombre": m.get("nombre"),
                "carpeta": m.get("carpeta"),
                "grupo": m.get("grupo"),
                "estado": m.get("estado"),
                "avance_pct": m.get("avance_pct", 0),
                "pendientes": m.get("pendientes") or [],
                "pendientes_n": len(m.get("pendientes") or []),
                "diagnostico": diag,
                "prioridad": prioridad,
            }
        )

    hecho = sum(1 for p in proyectos if p["estado"] == "hecho")
    parcial = sum(1 for p in proyectos if p["estado"] == "parcial")
    falta = sum(1 for p in proyectos if p["estado"] == "falta")
    total = len(proyectos)
    avance = round(sum(p["avance_pct"] for p in proyectos) / total) if total else 0
    pendientes_flat = [x for p in proyectos for x in p["pendientes"]]

    return {
        "id": capa_id,
        "titulo": info["titulo"],
        "subtitulo": info["subtitulo"],
        "total": total,
        "hecho": hecho,
        "parcial": parcial,
        "falta": falta,
        "avance_promedio": avance,
        "pendientes_total": len(pendientes_flat),
        "veredicto": _veredicto_capa(hecho, parcial, falta, total),
        "proyectos": proyectos,
        "bloqueadores": [p["nombre"] for p in proyectos if p["prioridad"] == "alta"][:6],
    }


def _sintesis(creador: dict, productos: dict, resumen: dict) -> str:
    parts = [
        f"**Creador de proyectos** ({creador['total']} módulos): "
        f"{creador['hecho']} listos, {creador['parcial']} parciales — veredicto *{creador['veredicto']}* "
        f"(avance medio {creador['avance_promedio']}%).",
        f"**Proyectos creados** ({productos['total']} pipelines): "
        f"{productos['hecho']} listos, {productos['parcial']} parciales — veredicto *{productos['veredicto']}* "
        f"(avance medio {productos['avance_promedio']}%).",
    ]
    if creador.get("bloqueadores"):
        parts.append(
            "Bloqueadores en la fábrica: "
            + ", ".join(f"**{b}**" for b in creador["bloqueadores"][:3])
            + "."
        )
    if productos.get("bloqueadores"):
        parts.append(
            "Bloqueadores en productos: "
            + ", ".join(f"**{b}**" for b in productos["bloqueadores"][:4])
            + "."
        )
    evals = resumen.get("evaluaciones", 0)
    cola = resumen.get("cola_pendientes", 0)
    if evals or cola:
        parts.append(
            f"Cola lluvia: **{cola}** sin revisar · **{evals}** evaluaciones de ideas."
        )
    return " ".join(parts)


def analisis_ecosistema(modulos: list[dict], resumen: dict | None = None) -> dict:
    resumen = resumen or {}
    mods_creador = [m for m in modulos if m.get("capa") == CAPA_CREADOR]
    mods_producto = [m for m in modulos if m.get("capa") == CAPA_PRODUCTO]

    creador = _analizar_capa(mods_creador, CAPA_CREADOR)
    productos = _analizar_capa(mods_producto, CAPA_PRODUCTO)

    todos = creador["proyectos"] + productos["proyectos"]
    prio_order = {"alta": 0, "media": 1, "baja": 2}
    top_prioridades = sorted(
        [p for p in todos if p["prioridad"] != "baja"],
        key=lambda p: (prio_order.get(p["prioridad"], 9), -p["pendientes_n"], -p["avance_pct"]),
    )[:8]

    avance_global = round((creador["avance_promedio"] + productos["avance_promedio"]) / 2)

    return {
        "generado_at": datetime.now(timezone.utc).isoformat(),
        "avance_global": avance_global,
        "sintesis": _sintesis(creador, productos, resumen),
        "capas": [creador, productos],
        "creador": creador,
        "productos": productos,
        "top_prioridades": top_prioridades,
        "totales": {
            "modulos": len(todos),
            "hecho": creador["hecho"] + productos["hecho"],
            "parcial": creador["parcial"] + productos["parcial"],
            "falta": creador["falta"] + productos["falta"],
            "pendientes_abiertas": creador["pendientes_total"] + productos["pendientes_total"],
        },
    }

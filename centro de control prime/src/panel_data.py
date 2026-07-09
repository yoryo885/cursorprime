"""Prepara datos para el panel — con textos de ayuda en español claro."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

from src.modulos import CAPA_CREADOR, CAPA_PRODUCTO, MODULO_SECCIONES

FLUJO_AYUDA = {
    1: {
        "nombre_corto": "Investigar mercado",
        "explicacion": "Miras YouTube y web para ver qué productos o nichos funcionan hoy.",
        "proyecto": "analisis-de-proyectos",
        "accion": "Carpeta: analisis-de-proyectos",
    },
    2: {
        "nombre_corto": "Lluvia de ideas",
        "explicacion": "El sistema propone mejoras y nuevas ideas. Tú decides: aprobar, posponer o rechazar.",
        "proyecto": "lluvia-de-ideas",
        "accion": "Carpeta: lluvia-de-ideas → cola",
    },
    3: {
        "nombre_corto": "Evaluar y diseñar",
        "explicacion": "Compruebas si una idea vale la pena y diseñas el proyecto antes de construir.",
        "proyecto": "ideas de proyectos",
        "accion": "Carpeta: ideas de proyectos",
    },
    4: {
        "nombre_corto": "Crear contenido",
        "explicacion": "Generas imágenes, packs visuales, videos o PDFs promocionales.",
        "proyecto": "creador de contenido",
        "accion": "Carpeta: creador de contenido",
    },
}

COLA_AYUDA = {
    "pendientes": {
        "titulo": "Pendientes de revisar",
        "explicacion": "Ideas nuevas que la lluvia generó y aún no has mirado.",
        "color": "#00e5ff",
    },
    "implementadas": {
        "titulo": "Ya construidas",
        "explicacion": "Aprobaste la idea y ya existe en cursorprime (código o pipeline hecho).",
        "color": "#00ff88",
    },
    "en_espera": {
        "titulo": "Pospuestas",
        "explicacion": "Te interesan pero dijiste «después» — no están descartadas.",
        "color": "#ffd54f",
    },
    "aprobadas": {
        "titulo": "Aprobadas (por hacer)",
        "explicacion": "Dijiste que sí, pero todavía no se implementaron.",
        "color": "#1a6dff",
    },
    "rechazadas": {
        "titulo": "Rechazadas",
        "explicacion": "Decidiste que no valía la pena seguir con esa idea.",
        "color": "#ff5252",
    },
}


def _cola_por_categoria(inv: dict) -> dict[str, int]:
    counts: Counter[str] = Counter()
    items = inv.get("cola_lluvia", {}).get("items", {})
    for estado_items in items.values():
        for it in estado_items:
            cat = it.get("categoria") or "otro"
            counts[cat] += 1
    return dict(counts.most_common())


def _eval_por_veredicto(inv: dict) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for ev in inv.get("evaluaciones", []):
        v = ev.get("estado") or "sin_veredicto"
        counts[v] += 1
    return dict(counts)


def _format_fecha(iso: str) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso[:16].replace("T", " ")


def prepare_panel_data(inv: dict) -> dict:
    r = inv.get("resumen", {})
    cola_counts = inv.get("cola_lluvia", {}).get("counts", {})
    total_cola = sum(cola_counts.values()) or 1
    impl = cola_counts.get("implementadas", 0)
    avance = min(100, round((impl / total_cola) * 100))

    flujo_enriquecido = []
    for p in inv.get("flujo", []):
        ayuda = FLUJO_AYUDA.get(p["paso"], {})
        flujo_enriquecido.append({**p, **ayuda})

    metricas = [
        {
            "id": "analisis",
            "titulo": "Investigaciones hechas",
            "valor": r.get("analisis", 0),
            "explicacion": "Cuántas veces investigaste un nicho o mercado (YouTube, web, KDP…).",
        },
        {
            "id": "implementadas",
            "titulo": "Ideas ya hechas",
            "valor": r.get("cola_implementadas", 0),
            "explicacion": "Ideas que aprobaste y ya están construidas en el ecosistema.",
        },
        {
            "id": "espera",
            "titulo": "Ideas pospuestas",
            "valor": r.get("cola_en_espera", 0),
            "explicacion": "Las guardaste para más adelante — siguen vivas en la cola.",
        },
        {
            "id": "pendientes",
            "titulo": "Sin revisar",
            "valor": r.get("cola_pendientes", 0),
            "explicacion": "Propuestas de la lluvia que aún no has mirado.",
        },
        {
            "id": "evaluaciones",
            "titulo": "Ideas evaluadas",
            "valor": r.get("evaluaciones", 0),
            "explicacion": "Ideas de negocio a las que ya les hiciste un veredicto (viable, condicional…).",
        },
        {
            "id": "carpetas",
            "titulo": "Carpetas en disco",
            "valor": r.get("carpetas_total", 0),
            "explicacion": "Proyectos y carpetas principales en ~/cursorprime.",
        },
        {
            "id": "modulos_ok",
            "titulo": "Módulos listos",
            "valor": r.get("modulos_hecho", 0),
            "explicacion": "Pipelines o capacidades con lo esencial implementado.",
        },
        {
            "id": "modulos_parcial",
            "titulo": "Módulos parciales",
            "valor": r.get("modulos_parcial", 0),
            "explicacion": "Funcionan en demo pero falta producción o cliente real.",
        },
        {
            "id": "clientes",
            "titulo": "Clientes carpeta",
            "valor": r.get("clientes_total", 0),
            "explicacion": "Carpetas en clientes/ (incluye demos ficticios).",
        },
    ]

    tabs_ayuda = {
        "analisis": "Investigaciones de mercado con fetch live/mock, fuentes, veredicto y enlace al informe.",
        "implementadas": "Ideas que dijiste sí y ya existen como código o pipeline en cursorprime.",
        "espera": "Ideas que pospusiste — puedes retomarlas cuando quieras.",
        "pendientes": "Propuestas nuevas de la lluvia. Aquí es donde suele tocar tu decisión.",
        "evaluaciones": "Ideas de negocio evaluadas con veredicto: viable, condicional, etc.",
        "contenido": "Material visual creado: packs promocionales, demos, lotes de imágenes.",
        "skills": "Habilidades instaladas en Cursor que el agente usa automáticamente.",
        "modulos": "Tu fábrica (creador de proyectos) separada de los pipelines que ya construiste.",
        "analisis_proyectos": "Viabilidad por proyecto — YouTube + web, mismo formato que el radar KDP.",
        "carpetas": "Árbol de carpetas principales del ecosistema.",
        "embudo": "Presencia digital: informe → propuesta → web → WhatsApp.",
        "clientes_tab": "Clientes con carpeta propia y proyectos activos.",
    }

    modulos = inv.get("modulos", [])
    modulos_secciones = []
    for capa_id in (CAPA_CREADOR, CAPA_PRODUCTO):
        info = MODULO_SECCIONES[capa_id]
        mods = [m for m in modulos if m.get("capa") == capa_id]
        modulos_secciones.append(
            {
                "id": capa_id,
                "titulo": info["titulo"],
                "subtitulo": info["subtitulo"],
                "modulos": mods,
                "count": len(mods),
            }
        )

    return {
        "generado_at": inv.get("generado_at", ""),
        "generado_legible": _format_fecha(inv.get("generado_at", "")),
        "avance": avance,
        "avance_explicacion": f"De {total_cola} ideas en la cola, {impl} ya están implementadas ({avance}%).",
        "resumen": r,
        "guia_intro": (
            "Este panel resume **todo lo que has creado** en cursorprime. "
            "No modifica nada — solo lee tus carpetas y te muestra en qué paso va cada cosa."
        ),
        "cola_counts": cola_counts,
        "cola_ayuda": COLA_AYUDA,
        "cola_labels": [COLA_AYUDA[k]["titulo"] for k in ("pendientes", "implementadas", "en_espera", "aprobadas", "rechazadas")],
        "cola_keys": list(COLA_AYUDA.keys()),
        "cola_values": [
            cola_counts.get("pendientes", 0),
            cola_counts.get("implementadas", 0),
            cola_counts.get("en_espera", 0),
            cola_counts.get("aprobadas", 0),
            cola_counts.get("rechazadas", 0),
        ],
        "flujo": flujo_enriquecido,
        "flujo_values": [p["count"] for p in inv.get("flujo", [])],
        "produccion_labels": ["Packs visuales", "Prompts", "Skills creadas", "Evaluaciones", "Borradores"],
        "produccion_explicacion": "Cosas que ya produjo el ecosistema — material, plantillas y borradores.",
        "produccion_values": [
            r.get("packs_contenido", 0),
            r.get("lotes_prompts", 0),
            r.get("skills_generadas", 0),
            r.get("evaluaciones", 0),
            r.get("borradores", 0),
        ],
        "metricas": metricas,
        "categorias": _cola_por_categoria(inv),
        "veredictos": _eval_por_veredicto(inv),
        "analisis": inv.get("analisis", []),
        "implementadas": inv.get("cola_lluvia", {}).get("items", {}).get("implementadas", []),
        "en_espera": inv.get("cola_lluvia", {}).get("items", {}).get("en_espera", []),
        "pendientes": inv.get("cola_lluvia", {}).get("items", {}).get("pendientes", []),
        "evaluaciones": inv.get("evaluaciones", []),
        "contenido": inv.get("contenido", []),
        "skills_instaladas": inv.get("skills_instaladas", []),
        "proyectos": inv.get("proyectos", []),
        "tabs_ayuda": tabs_ayuda,
        "carpetas": inv.get("carpetas", []),
        "modulos": modulos,
        "modulos_secciones": modulos_secciones,
        "modulos_creador": [m for m in modulos if m.get("capa") == CAPA_CREADOR],
        "modulos_productos": [m for m in modulos if m.get("capa") == CAPA_PRODUCTO],
        "analisis_ecosistema": inv.get("analisis_ecosistema", {}),
        "viabilidad_proyectos": inv.get("viabilidad_proyectos", {}),
        "modulos_resumen": inv.get("modulos_resumen", {}),
        "embudo_comercial": inv.get("embudo_comercial", []),
        "embudo_index": inv.get("embudo_index", ""),
        "embudo_produccion": inv.get("embudo_produccion", {}),
        "prospeccion": inv.get("prospeccion", {}),
        "rentabilidad": inv.get("rentabilidad", {}),
        "clientes": inv.get("clientes", []),
        "analisis_detalle": inv.get("analisis_detalle", []),
        "analisis_ultimo": inv.get("analisis_ultimo"),
        "radar_auto": inv.get("radar_auto", {}),
        "radar_historial": inv.get("radar_historial", []),
        "modulos_chart_labels": ["Listo", "Parcial", "Por hacer"],
        "modulos_chart_values": [
            inv.get("modulos_resumen", {}).get("hecho", 0),
            inv.get("modulos_resumen", {}).get("parcial", 0),
            inv.get("modulos_resumen", {}).get("falta", 0),
        ],
        "embudo_labels": [f"Paso {e['paso']}" for e in inv.get("embudo_comercial", [])],
        "embudo_values": [100 if e.get("listo") else 30 for e in inv.get("embudo_comercial", [])],
    }

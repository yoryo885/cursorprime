"""Contenido comercial del PDF: portada, guía, empieza aquí y checklist."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.output_paths import meta_dir
from src.serie import (
    hook_para_rol,
    label_portada,
    subtitulo_portada,
    titulo_comercial,
)

PRODUCTO_FILENAME = "producto.json"


@dataclass
class ProductExtras:
    titulo_comercial: str = ""
    subtitulo_portada: str = ""
    serie_nombre: str = ""
    imagen_portada: str = ""
    mini_guia: list[str] = field(default_factory=list)
    empieza_pasos: list[str] = field(default_factory=list)
    checklist_titulo: str = "¿Estoy aplicando Pareto?"
    checklist_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ProductExtras:
        return cls(
            titulo_comercial=str(data.get("titulo_comercial", "") or ""),
            subtitulo_portada=str(data.get("subtitulo_portada", "") or ""),
            serie_nombre=str(data.get("serie_nombre", "") or ""),
            imagen_portada=str(data.get("imagen_portada", "") or ""),
            mini_guia=[str(x) for x in data.get("mini_guia", []) if x],
            empieza_pasos=[str(x) for x in data.get("empieza_pasos", []) if x],
            checklist_titulo=str(data.get("checklist_titulo") or "¿Estoy aplicando Pareto?"),
            checklist_items=[str(x) for x in data.get("checklist_items", []) if x],
        )


def producto_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / PRODUCTO_FILENAME


def load_product_extras(output_dir: Path) -> ProductExtras | None:
    path = producto_path(output_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        extras = ProductExtras.from_dict(data)
        if extras.titulo_comercial or extras.mini_guia or extras.checklist_items:
            return extras
    except (OSError, json.JSONDecodeError):
        pass
    return None


def save_product_extras(output_dir: Path, extras: ProductExtras) -> Path:
    path = producto_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(extras.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _format_oficio(audiencia: str) -> str:
    from src.serie import rol_plural

    return rol_plural(audiencia)


def _concepto_corto(libro_nombre: str) -> str:
    from src.serie import concepto_corto

    return concepto_corto(libro_nombre)


def default_product_extras(
    *,
    libro_nombre: str,
    audiencia: str = "",
    num_semanas: int = 10,
    familia_rol: str = "",
    reto: str = "",
    hook: str = "",
) -> ProductExtras:
    concepto = _concepto_corto(libro_nombre)

    return ProductExtras(
        titulo_comercial=titulo_comercial(
            libro_nombre=libro_nombre,
            audiencia=audiencia,
            familia_rol=familia_rol,
            reto=reto,
            hook=hook,
        ),
        subtitulo_portada=subtitulo_portada(libro_nombre),
        serie_nombre=label_portada(),
        mini_guia=[
            "Lee un tema por vez; no intentes aplicar todo el mismo lunes.",
            "Al final del PDF tienes un plan semanal listo para imprimir.",
            "Una semana = una acción. Marca ✓ solo cuando haya evidencia real.",
            "Usa la columna NOTAS del plan para anotar tus resultados medibles.",
            "Si dudas, vuelve al mapa conceptual antes de la semana 1.",
        ],
        empieza_pasos=[
            'Lee «Para quién es este resumen» y el aviso legal (2 minutos).',
            "Elige 2 casos críticos de tu carga actual y anótalos en papel.",
            "Abre la Semana 01 del plan de acción y complétala esta semana.",
        ],
        checklist_titulo=f"¿Estoy aplicando {concepto}?",
        checklist_items=[
            "Identifiqué mis casos críticos (el 20%) esta semana",
            "Dediqué más tiempo e energía a esos casos que al resto",
            "Eliminé o reduje al menos una tarea de bajo impacto",
            "Registré un resultado medible (tiempo, avance, derivaciones…)",
            "Documenté el resultado en mi registro o NOTAS del plan",
            "Revisé si los casos prioritarios siguen siendo los mismos",
            "Coordiné con docentes o familia solo en casos vitales",
            "Protegí un bloque de tiempo para intervención profunda",
            "No dispersé esfuerzo en urgencias que otros pueden resolver",
            "Cerré la semana sabiendo qué haré distinto la próxima",
        ],
    )


def ensure_product_extras(
    output_dir: Path,
    *,
    libro_nombre: str,
    audiencia: str = "",
    num_semanas: int = 10,
    familia_rol: str = "",
    reto: str = "",
    hook: str = "",
) -> ProductExtras:
    existing = load_product_extras(output_dir)
    if existing:
        return existing
    extras = default_product_extras(
        libro_nombre=libro_nombre,
        audiencia=audiencia,
        num_semanas=num_semanas,
        familia_rol=familia_rol,
        reto=reto,
        hook=hook,
    )
    save_product_extras(output_dir, extras)
    return extras

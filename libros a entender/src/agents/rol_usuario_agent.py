"""Agente que define ROL_USUARIO para oficios nuevos (fuera de plantillas)."""
from __future__ import annotations

import json
import re
from typing import Any

from src.rol_usuario import (
    RolProfile,
    classify_familia,
    profile_from_familia,
    profile_generico,
    rol_slug,
    save_to_roles_catalog,
)


class RolUsuarioAgent:
    """
    Cuando el oficio no encaja en las 5 familias predefinidas, este agente
    genera léxico, KPIs, metodología y términos prohibidos del dominio.
    Guarda el resultado en el catálogo global para reutilizarlo en otros libros.
    """

    REFERENCIA_FAMILIAS = """
Ejemplos de calidad (estructura, no copies el dominio):
- Inversionista/Emprendedor → capital, riesgo-beneficio, activos, escalabilidad
- Psicopedagoga/Educador → cognición, hitos de aprendizaje, plasticidad, KPIs individuales
- Ingeniero/Técnico → precisión, procesos, fallas, robustez estructural
- Profesional de Salud → triage, urgencias, diagnóstico, eficiencia de recursos
- Creativo/Artista → impacto visual, narrativa de marca, estatus, resonancia emocional
"""

    def __init__(self, llm):
        self.llm = llm

    def run(
        self,
        rol_usuario: str,
        *,
        reto: str = "",
        intento_fallido: str = "",
        brief: str = "",
    ) -> RolProfile:
        rol_usuario = (rol_usuario or "").strip()
        if not rol_usuario:
            return RolProfile(rol_usuario="", familia_rol="", enfoque="")

        familia = classify_familia(rol_usuario)
        if familia:
            profile = profile_from_familia(
                familia,
                rol_usuario,
                reto=reto,
                intento_fallido=intento_fallido,
            )
            save_to_roles_catalog(profile)
            return profile

        print(f"   🎭 RolUsuarioAgent: perfil nuevo para «{rol_usuario}»...")
        profile = self._generar_con_llm(
            rol_usuario,
            reto=reto,
            intento_fallido=intento_fallido,
            brief=brief,
        )
        save_to_roles_catalog(profile)
        print(
            f"      ✓ familia «{profile.familia_rol}» · "
            f"{len(profile.lexico)} términos · {len(profile.kpis)} KPIs"
        )
        return profile

    def _generar_con_llm(
        self,
        rol_usuario: str,
        *,
        reto: str,
        intento_fallido: str,
        brief: str,
    ) -> RolProfile:
        brief_block = f"\nContexto del pedido: «{brief}»\n" if brief else ""
        prompt = f"""Eres el AGENTE ROL_USUARIO de un sistema de resúmenes PDF por oficio.

Tu función es adaptar lenguaje, KPIs y metodología de resolución de problemas
según el oficio del lector.

ROL_USUARIO = {rol_usuario}
Reto del lector: {reto or "no indicado"}
Lo que intentó sin éxito: {intento_fallido or "no indicado"}
{brief_block}
{self.REFERENCIA_FAMILIAS}

Genera un perfil ESPECÍFICO para «{rol_usuario}» con el mismo nivel de detalle
que los ejemplos. No uses alternativas genéricas ni lenguaje de otro dominio.

Responde SOLO JSON válido con estas claves:
- familia_rol: slug snake_case único para este oficio (ej. chef_cocina, abogado_laboral)
- enfoque: una frase con el ángulo profesional de éxito
- lexico: array de 6-10 términos reales del oficio (jerga laboral concreta)
- kpis: array de 4-6 métricas observables de éxito en ese trabajo
- metodologia: cadena con 3-5 pasos de resolución de problemas del oficio (usa →)
- prohibido: array de 4-8 términos de OTROS dominios que confundirían al lector

Regla: léxico y KPIs del dominio real de {rol_usuario}. Sin autoayuda vacía."""

        try:
            raw = self.llm.call(prompt)
            data = self._parse_json(raw)
            if not data:
                return profile_generico(
                    rol_usuario, reto=reto, intento_fallido=intento_fallido
                )
            return RolProfile(
                rol_usuario=rol_usuario,
                familia_rol=str(data.get("familia_rol") or rol_slug(rol_usuario)),
                enfoque=str(data.get("enfoque") or ""),
                lexico=[str(x) for x in data.get("lexico", []) if x],
                kpis=[str(x) for x in data.get("kpis", []) if x],
                metodologia=str(data.get("metodologia") or ""),
                prohibido=[str(x) for x in data.get("prohibido", []) if x],
                reto=reto,
                intento_fallido=intento_fallido,
            )
        except Exception as exc:
            print(f"      ⚠️  RolUsuarioAgent falló: {exc}")
            return profile_generico(
                rol_usuario, reto=reto, intento_fallido=intento_fallido
            )

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any] | None:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group())
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None

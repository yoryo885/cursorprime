"""Perfil ROL_USUARIO: léxico, KPIs y metodología por oficio del lector."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.output_paths import meta_dir

ROL_PERFIL_FILENAME = "rol_perfil.json"

# Familias de rol con plantillas del prompt editorial
ROLE_FAMILIES: dict[str, dict[str, Any]] = {
    "inversionista_emprendedor": {
        "keywords": (
            "inversionista",
            "inversor",
            "emprendedor",
            "startup",
            "founder",
            "negocio",
            "empresa",
            "ceo",
            "director general",
        ),
        "enfoque": (
            "eficiencia de capital, riesgo-beneficio, optimización de activos y escalabilidad"
        ),
        "lexico": [
            "capital",
            "ROI",
            "margen",
            "activos",
            "escalabilidad",
            "runway",
            "unit economics",
            "riesgo",
        ],
        "kpis": [
            "retorno sobre inversión",
            "costo de adquisición",
            "margen neto",
            "tiempo de recuperación del capital",
        ],
        "metodologia": (
            "evaluar riesgo-beneficio → priorizar activos de alto retorno → "
            "eliminar gasto de bajo impacto → escalar lo que funciona"
        ),
        "prohibido": [
            "aula",
            "estudiante",
            "paciente",
            "diagnóstico clínico",
            "paleta de colores",
        ],
    },
    "psicopedagoga_educador": {
        "keywords": (
            "psicopedagog",
            "pedagog",
            "educador",
            "docente",
            "maestro",
            "profesor",
            "orientador",
            "escuela",
            "aula",
            "alumno",
            "estudiante",
        ),
        "enfoque": (
            "procesos cognitivos, hitos de aprendizaje, plasticidad neuronal "
            "y KPIs de desempeño individual"
        ),
        "lexico": [
            "procesos cognitivos",
            "hitos de aprendizaje",
            "intervención",
            "seguimiento",
            "gabinete",
            "aula",
            "plasticidad",
        ],
        "kpis": [
            "avance lector",
            "autonomía en aula",
            "reducción de derivaciones",
            "tiempo por caso crítico",
        ],
        "metodologia": (
            "triaje de casos → priorizar por impacto en aprendizaje → "
            "intervención focalizada → registro de avances"
        ),
        "prohibido": [
            "clientes",
            "ventas",
            "ROI de negocio",
            "activos financieros",
            "escalabilidad comercial",
        ],
    },
    "ingeniero_tecnico": {
        "keywords": (
            "ingenier",
            "técnico",
            "tecnico",
            "desarrollador",
            "devops",
            "sistemas",
            "mecánic",
            "electricista",
            "soldador",
            "programador",
        ),
        "enfoque": (
            "precisión, optimización de procesos, reducción de fallas y robustez estructural"
        ),
        "lexico": [
            "proceso",
            "falla",
            "tolerancia",
            "robustez",
            "optimización",
            "especificación",
            "mantenimiento",
        ],
        "kpis": [
            "tasa de fallas",
            "tiempo de ciclo",
            "uptime",
            "desviación respecto a especificación",
        ],
        "metodologia": (
            "medir → identificar cuellos de botella → reducir variabilidad → "
            "reforzar puntos críticos del sistema"
        ),
        "prohibido": [
            "aula",
            "paciente",
            "narrativa de marca",
            "portafolio de inversión",
        ],
    },
    "profesional_salud": {
        "keywords": (
            "salud",
            "médic",
            "medic",
            "enfermer",
            "fisioterapeut",
            "psicólog",
            "psicolog",
            "clínic",
            "hospital",
            "paciente",
            "urgencias",
        ),
        "enfoque": (
            "protocolos de triage, manejo de urgencias, precisión diagnóstica "
            "y eficiencia de recursos"
        ),
        "lexico": [
            "triage",
            "protocolo",
            "urgencia",
            "diagnóstico",
            "recursos",
            "intervención",
            "seguimiento clínico",
        ],
        "kpis": [
            "tiempo hasta intervención",
            "precisión diagnóstica",
            "uso eficiente de recursos",
            "resultados por paciente",
        ],
        "metodologia": (
            "triage → priorizar por urgencia e impacto → protocolo focalizado → "
            "seguimiento de resultados"
        ),
        "prohibido": [
            "clientes",
            "ventas",
            "ROI comercial",
            "métricas de redes sociales",
        ],
    },
    "creativo_artista": {
        "keywords": (
            "creativ",
            "artista",
            "diseñador",
            "diseñador",
            "fotógraf",
            "ilustrador",
            "marca",
            "branding",
            "copywriter",
            "publicista",
        ),
        "enfoque": (
            "impacto visual, narrativa de marca, estatus y resonancia emocional táctica"
        ),
        "lexico": [
            "impacto visual",
            "narrativa",
            "marca",
            "estatus",
            "resonancia emocional",
            "identidad",
            "audiencia",
        ],
        "kpis": [
            "engagement",
            "recordación de marca",
            "conversión emocional",
            "coherencia visual",
        ],
        "metodologia": (
            "definir mensaje central → priorizar activos de alto impacto visual → "
            "refinar narrativa → medir resonancia"
        ),
        "prohibido": [
            "protocolo clínico",
            "triage hospitalario",
            "derivación escolar",
            "balance general contable",
        ],
    },
}


@dataclass
class RolProfile:
    rol_usuario: str
    familia_rol: str
    enfoque: str
    lexico: list[str] = field(default_factory=list)
    kpis: list[str] = field(default_factory=list)
    metodologia: str = ""
    prohibido: list[str] = field(default_factory=list)
    reto: str = ""
    intento_fallido: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RolProfile:
        return cls(
            rol_usuario=str(data.get("rol_usuario", "") or ""),
            familia_rol=str(data.get("familia_rol", "") or ""),
            enfoque=str(data.get("enfoque", "") or ""),
            lexico=[str(x) for x in data.get("lexico", []) if x],
            kpis=[str(x) for x in data.get("kpis", []) if x],
            metodologia=str(data.get("metodologia", "") or ""),
            prohibido=[str(x) for x in data.get("prohibido", []) if x],
            reto=str(data.get("reto", "") or ""),
            intento_fallido=str(data.get("intento_fallido", "") or ""),
        )


def rol_perfil_path(output_dir: Path) -> Path:
    return meta_dir(output_dir) / ROL_PERFIL_FILENAME


def classify_familia(audiencia: str) -> str | None:
    texto = (audiencia or "").lower()
    if not texto:
        return None
    for familia, cfg in ROLE_FAMILIES.items():
        for kw in cfg["keywords"]:
            if kw in texto:
                return familia
    return None


def profile_from_familia(
    familia: str,
    rol_usuario: str,
    *,
    reto: str = "",
    intento_fallido: str = "",
) -> RolProfile:
    cfg = ROLE_FAMILIES.get(familia, {})
    return RolProfile(
        rol_usuario=rol_usuario,
        familia_rol=familia,
        enfoque=str(cfg.get("enfoque", "")),
        lexico=list(cfg.get("lexico", [])),
        kpis=list(cfg.get("kpis", [])),
        metodologia=str(cfg.get("metodologia", "")),
        prohibido=list(cfg.get("prohibido", [])),
        reto=reto,
        intento_fallido=intento_fallido,
    )


def rol_slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (text or "").lower().strip())
    return slug[:60] or "rol"


def roles_catalog_path() -> Path:
    from src.config import ROLES_CATALOG_PATH

    return ROLES_CATALOG_PATH


def load_roles_catalog() -> dict[str, dict[str, Any]]:
    path = roles_catalog_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_to_roles_catalog(profile: RolProfile) -> Path:
    """Guarda el perfil en catálogo global para reutilizar en otros libros."""
    if not profile.rol_usuario:
        return roles_catalog_path()

    catalog = load_roles_catalog()
    key = rol_slug(profile.rol_usuario)
    catalog[key] = profile.to_dict()
    path = roles_catalog_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def lookup_roles_catalog(rol_usuario: str) -> RolProfile | None:
    """Busca un oficio ya definido en el catálogo global."""
    rol_usuario = (rol_usuario or "").strip()
    if not rol_usuario:
        return None

    catalog = load_roles_catalog()
    key = rol_slug(rol_usuario)
    if key in catalog:
        return RolProfile.from_dict(catalog[key])

    texto = rol_usuario.lower()
    for entry in catalog.values():
        if str(entry.get("rol_usuario", "")).lower() == texto:
            return RolProfile.from_dict(entry)
    return None


def profile_generico(
    rol_usuario: str,
    *,
    reto: str = "",
    intento_fallido: str = "",
) -> RolProfile:
    return RolProfile(
        rol_usuario=rol_usuario,
        familia_rol="personalizado",
        enfoque=(
            f"objetivos concretos de éxito en el trabajo de {rol_usuario}, "
            "con métricas observables y metodología aplicable esta semana"
        ),
        lexico=[rol_usuario, "intervención", "priorización", "impacto", "seguimiento"],
        kpis=["tiempo invertido vs. impacto real", "resultados medibles esta semana"],
        metodologia=(
            "diagnosticar → priorizar lo crítico → actuar con foco → medir avance"
        ),
        prohibido=["clientes genéricos", "ventas", "ROI", "autoayuda vacía"],
        reto=reto,
        intento_fallido=intento_fallido,
    )


def infer_profile_llm(
    llm,
    rol_usuario: str,
    *,
    reto: str = "",
    intento_fallido: str = "",
    brief: str = "",
) -> RolProfile:
    from src.agents.rol_usuario_agent import RolUsuarioAgent

    return RolUsuarioAgent(llm).run(
        rol_usuario,
        reto=reto,
        intento_fallido=intento_fallido,
        brief=brief,
    )


def build_rol_profile(
    rol_usuario: str,
    *,
    reto: str = "",
    intento_fallido: str = "",
    llm=None,
    brief: str = "",
) -> RolProfile:
    rol_usuario = (rol_usuario or "").strip()
    if not rol_usuario:
        return RolProfile(rol_usuario="", familia_rol="", enfoque="")

    cached = lookup_roles_catalog(rol_usuario)
    if cached:
        print(f"   📚 ROL_USUARIO reutilizado del catálogo: «{rol_usuario}»")
        return RolProfile(
            rol_usuario=rol_usuario,
            familia_rol=cached.familia_rol,
            enfoque=cached.enfoque,
            lexico=list(cached.lexico),
            kpis=list(cached.kpis),
            metodologia=cached.metodologia,
            prohibido=list(cached.prohibido),
            reto=reto or cached.reto,
            intento_fallido=intento_fallido or cached.intento_fallido,
        )

    familia = classify_familia(rol_usuario)
    if familia:
        profile = profile_from_familia(
            familia, rol_usuario, reto=reto, intento_fallido=intento_fallido
        )
        save_to_roles_catalog(profile)
        return profile

    if llm:
        return infer_profile_llm(
            llm,
            rol_usuario,
            reto=reto,
            intento_fallido=intento_fallido,
            brief=brief,
        )
    return profile_generico(rol_usuario, reto=reto, intento_fallido=intento_fallido)


def _brief_from_plan(output_dir: Path) -> str:
    try:
        from src.agents.planner_agent import BookPlan, plan_path_for

        plan = BookPlan.from_dict(
            json.loads(plan_path_for(output_dir).read_text(encoding="utf-8"))
        )
        return plan.brief or ""
    except (FileNotFoundError, json.JSONDecodeError, OSError, ImportError):
        return ""


def ensure_rol_perfil(output_dir: Path, llm=None, *, force: bool = False) -> RolProfile | None:
    output_dir = Path(output_dir)
    audiencia, reto, intento = _ctx_from_output(output_dir)
    if not audiencia:
        return None

    existing = load_rol_perfil(output_dir)
    audiencia_ok = (
        existing
        and existing.rol_usuario.strip().lower() == audiencia.strip().lower()
    )
    if not force and audiencia_ok:
        return existing

    if audiencia_ok is False and existing:
        print(
            f"   🎭 Audiencia cambió ({existing.rol_usuario} → {audiencia}); "
            "regenerando ROL_USUARIO..."
        )

    brief = _brief_from_plan(output_dir)
    profile = build_rol_profile(
        audiencia,
        reto=reto,
        intento_fallido=intento,
        llm=llm,
        brief=brief,
    )
    save_rol_perfil(output_dir, profile)
    return profile


def load_rol_perfil(output_dir: Path) -> RolProfile | None:
    path = rol_perfil_path(output_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = RolProfile.from_dict(data)
        return profile if profile.rol_usuario else None
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def save_rol_perfil(output_dir: Path, profile: RolProfile) -> Path:
    path = rol_perfil_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(profile.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _ctx_from_output(output_dir: Path) -> tuple[str, str, str]:
    from src.audiencia_context import load_audiencia_context

    ctx = load_audiencia_context(output_dir)
    audiencia = ctx.get("audiencia", "")
    return audiencia, ctx.get("reto", ""), ctx.get("intento_fallido", "")


_AGENT_HINTS: dict[str, str] = {
    "resumen": (
        "Traduce cada idea del PDF al dominio del ROL_USUARIO. "
        "Voz: segunda persona (tú). No hables como autor del resumen."
    ),
    "idea_clave": (
        "La idea debe incluir un KPI u objetivo de éxito concreto del rol."
    ),
    "ejemplo": (
        "Escena en «tú» aplicando la metodología del rol en su entorno laboral. "
        "Varía la situación dentro del mismo oficio (no cambies de profesión)."
    ),
    "aplicacion": (
        "Plan imperativo en «tú» con KPIs medibles del rol para esta semana."
    ),
    "intro": (
        "Explica por qué el resumen encaja con los KPIs y el trabajo del rol."
    ),
    "corrector": (
        "Preserva léxico y KPIs del rol; elimina lenguaje genérico o de otros dominios."
    ),
    "qc": (
        "Verifica léxico, KPIs y metodología del rol en ejemplos y aplicaciones."
    ),
}


def build_rol_block(profile: RolProfile | None, *, agent: str = "resumen") -> str:
    if not profile or not profile.rol_usuario:
        return ""

    lines = [
        f"**ROL_USUARIO = {profile.rol_usuario}**",
        "",
        "Adaptación obligatoria para este rol:",
        f"- Enfoque: {profile.enfoque}",
        f"- Léxico preferido: {', '.join(profile.lexico)}",
        f"- KPIs de éxito: {', '.join(profile.kpis)}",
        f"- Metodología: {profile.metodologia}",
    ]
    if profile.prohibido:
        lines.append(
            f"- Prohibido (lenguaje ajeno al rol): {', '.join(profile.prohibido)}"
        )
    if profile.reto:
        lines.append(f"- Reto del lector: {profile.reto}")
    if profile.intento_fallido:
        lines.append(f"- Lo que intentó sin éxito: {profile.intento_fallido}")

    lines.extend(
        [
            "",
            "Regla de ejecución: analiza el caso con léxico y objetivos de éxito "
            "del rol seleccionado. No ofrezcas alternativas genéricas; ofrece "
            "soluciones de alto rendimiento específicas para ese dominio.",
        ]
    )

    hint = _AGENT_HINTS.get(agent, "")
    if hint:
        lines.extend(["", hint])

    return "\n".join(lines)

"""Validaciones automáticas del plan de acción semanal."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.action_plan import ActionPlan, ActionPlanRow

MIN_ACCION_CHARS = 25
MIN_ACCION_WORDS = 6
MAX_ACCION_WORDS = 32
MAX_ACCION_CHARS = 200

FORMATO_ACCION = (
    "Formato OBLIGATORIO: 2 o 3 pasos cortos separados por « · ». "
    "Ejemplo: «Audita tu registro del mes · Marca los casos críticos · "
    "Registra: cuántas derivaciones evitaste esta semana». "
    "Máximo 28 palabras. Plantilla reutilizable cada semana."
)

EJEMPLOS_KPI_MEDIBLE = (
    "Registra: cuántas derivaciones evitaste · "
    "Mide: minutos por caso crítico · "
    "Registra: casos con avance lector documentado · "
    "Mide: autonomía en aula (escala 1-5)"
)

KPI_VAGOS = (
    r"\bobjetivos?\s+(mensuales?\s+)?cumplidos\b",
    r"\bavance\s+verificable\b",
    r"\bprogreso\s+en\s+hito\s+clave\b",
    r"\bcambio\s+observable\b",
    r"\btiempo\s+ganado\b",
    r"\bhoras\s+liberadas\b",
    r"\bun\s+kpi\b",
    r"\bkpi\s+del\s+rol\b",
    r"\bresultados?\s+medibles?\b",
    r"\bevidencia\s+observable\b",
    r"\bimpacto\s+real\b",
)

MEDIBLE_INDICADORES = (
    r"\bcuánt",
    r"\bnumero\b",
    r"\bnº\b",
    r"\bconteo\b",
    r"\bveces\b",
    r"\bminutos\b",
    r"\bderivaciones?\s+evitadas\b",
    r"\bcasos?\s+con\b",
    r"\bantes/después\b",
    r"\bregistro\s+de\b",
    r"\bescala\b",
    r"\bsubió\b",
    r"\bbajó\b",
    r"\bdocumentad",
    r"\besta\s+semana\b",
)

CIFRAS_PATRONES = (
    r"\bsupongamos\b",
    r"\b\d+\s*%",
    r"\b\d+\s+(estudiantes|casos|horas|sesiones|semanas|minutos|días|meses)\b",
    r"\bde\s+(los|las)\s+\d+\b",
    r"\b\d+\s+de\s+(tus|los|las)\s+\d+\b",
    r"\b(cincuenta|cuarenta|treinta|veinte|quince|diez|ocho|siete|seis|cinco|cuatro|tres)\s+(estudiantes|casos|horas)\b",
)

REPETICION_APERTURAS = (
    r"^\s*(revisa|marca|identifica|bloquea|blinda|ordena|lista|extrae|clasifica)\b",
    r"\b(franjas?|bloques?) (fijas?|semanales?|exclusiv)",
    r"\blibera(r)?\s+\d+\s+horas\b",
)

ESCENARIO_PATRONES: dict[str, tuple[str, ...]] = {
    "gabinete": (r"\bgabinete\b", r"\bpsicopedag"),
    "aula": (r"\baula\b", r"\bclase\b"),
    "familia": (r"\bfamili", r"\bpadres?\b", r"\bmadre\b", r"\babuel"),
    "equipo docente": (r"\bdocentes?\b", r"\bequipo docente\b", r"\btutor\b", r"\borientador"),
    "registro": (r"\bregistro\b", r"\bseguimiento\b", r"\bexpediente\b", r"\bficha\b"),
    "taller": (r"\btaller\b", r"\bplanta\b", r"\bobra\b"),
    "proceso": (r"\bproceso\b", r"\bprotocolo\b"),
    "cliente": (r"\bcliente\b", r"\busuario\b"),
    "finanzas": (r"\bfinanzas\b", r"\bcostos\b", r"\bventas\b"),
    "operación": (r"\boperaci", r"\brutina\b"),
    "reunión": (r"\breuni", r"\bequipo\b"),
    "espacio": (r"\bescritorio\b", r"\bespacio\b", r"\btrabajo\b"),
}

CONCEPTO_RAICES = (
    "prioriz",
    "identif",
    "concentr",
    "impacto",
    "intervenc",
    "transform",
    "crisis",
    "urgent",
    "casos",
    "energ",
    "elimina",
    "mapa",
)

STOPWORDS = frozenset(
    {
        "todos",
        "todas",
        "donde",
        "cuando",
        "porque",
        "estudiantes",
        "estudiante",
        "genera",
        "necesitan",
        "requieren",
        "misma",
        "mismo",
        "real",
        "debes",
        "deja",
        "dejar",
    }
)

FUERA_ROL_GENERICO = (
    r"\binformes?\s+judicial",
    r"\binspección\b",
    r"\bbatería\s+neuropsicológica\s+completa",
    r"\bsuscriptor",
    r"\bengagement\b",
    r"\bROI\b",
    r"\bclientes?\b",
    r"\bvideos?\b",
    r"\bcontenidos?\s+de\s+redes\b",
    r"\b métricas de redes\b",
)


@dataclass
class ActionPlanIssue:
    severity: str  # error | warning
    cargo: str
    tema: str
    message: str


@dataclass
class ActionPlanQCResult:
    passed: bool
    issues: list[ActionPlanIssue] = field(default_factory=list)

    def temas_con_errores(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for issue in self.issues:
            if issue.severity != "error" or not issue.tema or issue.tema in seen:
                continue
            seen.add(issue.tema)
            out.append(issue.tema)
        return out


def accion_truncada(texto: str) -> bool:
    t = (texto or "").strip()
    if len(t) < MIN_ACCION_CHARS:
        return True
    if re.search(r"\b(innegoc|incomplet|\.\.\.)$", t, re.I):
        return True
    return False


def accion_muy_corta(texto: str) -> bool:
    return len((texto or "").split()) < MIN_ACCION_WORDS


def accion_muy_larga(texto: str) -> bool:
    t = (texto or "").strip()
    return len(t.split()) > MAX_ACCION_WORDS or len(t) > MAX_ACCION_CHARS


def tiene_cifras_inventadas(texto: str) -> bool:
    t = (texto or "").lower()
    return any(re.search(pat, t, re.I) for pat in CIFRAS_PATRONES)


def pasos_accion(texto: str) -> list[str]:
    return [p.strip() for p in (texto or "").split("·") if p.strip()]


def formato_practico_ok(texto: str) -> bool:
    pasos = pasos_accion(texto)
    if len(pasos) < 2 or len(pasos) > 4:
        return False
    return all(len(p.split()) <= 12 for p in pasos)


def _apertura_normalizada(texto: str) -> str:
    t = (texto or "").lower().strip()
    t = re.sub(r"\d+", "N", t)
    return t[:55]


def filas_repetitivas(filas: list[ActionPlanRow]) -> list[str]:
    """Temas cuya apertura coincide con otra fila (mismo patrón narrativo)."""
    repetidos: list[str] = []
    aperturas: dict[str, str] = {}
    for row in filas:
        key = _apertura_normalizada(row.accion_concreta)
        if key in aperturas and aperturas[key] != row.tema:
            repetidos.append(row.tema)
        else:
            aperturas[key] = row.tema

    patrones_vistos: dict[str, int] = {}
    for row in filas:
        t = (row.accion_concreta or "").lower()
        for pat in REPETICION_APERTURAS:
            if re.search(pat, t):
                patrones_vistos[pat] = patrones_vistos.get(pat, 0) + 1
                if patrones_vistos[pat] >= 3 and row.tema not in repetidos:
                    repetidos.append(row.tema)
    return repetidos


def terminos_fuera_rol(texto: str, prohibido: list[str] | None = None) -> list[str]:
    found: list[str] = []
    t = (texto or "").lower()
    for pat in FUERA_ROL_GENERICO:
        if re.search(pat, t, re.I):
            found.append(pat)
    for term in prohibido or []:
        if term.lower() in t and term.lower() not in found:
            found.append(term)
    return found


def kpi_presente(texto: str, kpis: list[str]) -> bool:
    if not kpis:
        return True
    t = (texto or "").lower()
    for kpi in kpis:
        if kpi.lower() in t:
            return True
        palabras = [p for p in re.split(r"\W+", kpi.lower()) if len(p) > 4]
        if palabras and any(p in t for p in palabras):
            return True
    return False


def ultimo_paso_kpi(texto: str) -> str:
    pasos = pasos_accion(texto)
    return pasos[-1] if pasos else ""


def _contenido_kpi(ultimo_paso: str) -> str:
    return re.sub(r"^\s*(registra|mide)\s*:\s*", "", (ultimo_paso or "").lower(), flags=re.I)


def kpi_es_vago(ultimo_paso: str) -> bool:
    t = (ultimo_paso or "").lower().strip()
    if not re.match(r"^(registra|mide)\s*:", t):
        return True
    contenido = _contenido_kpi(t)
    return any(re.search(pat, contenido, re.I) for pat in KPI_VAGOS)


def kpi_tiene_unidad_medible(ultimo_paso: str, kpis: list[str]) -> bool:
    contenido = _contenido_kpi(ultimo_paso)
    if not contenido.strip():
        return False
    if any(re.search(pat, contenido, re.I) for pat in MEDIBLE_INDICADORES):
        return True
    for kpi in kpis:
        k = kpi.lower()
        if k in contenido and len(k.split()) >= 3:
            return True
    return False


def kpi_medible_ok(texto: str, kpis: list[str]) -> bool:
    """Último paso con Registra:/Mide:, KPI del rol y unidad contable u observable."""
    if not kpis:
        return True
    ultimo = ultimo_paso_kpi(texto)
    if not ultimo or kpi_es_vago(ultimo):
        return False
    if not kpi_presente(texto, kpis):
        return False
    return kpi_tiene_unidad_medible(ultimo, kpis)


def _palabras_clave(texto: str, *, min_len: int = 5) -> set[str]:
    return {
        w
        for w in re.findall(r"\w+", (texto or "").lower())
        if len(w) >= min_len and w not in STOPWORDS
    }


def escenario_presente(texto: str, escenario: str) -> bool:
    if not escenario:
        return True
    t = (texto or "").lower()
    e = escenario.lower()
    for key, pats in ESCENARIO_PATRONES.items():
        if key in e:
            return any(re.search(p, t, re.I) for p in pats)
    return e.split()[0] in t if e.split() else False


def concepto_anclado(texto: str, idea_clave: str, concepto_libro: str = "") -> bool:
    if concepto_libro and len(concepto_libro.strip()) >= 12:
        t = (texto or "").lower()
        claves = _palabras_clave(concepto_libro, min_len=4)
        if claves and sum(1 for c in claves if c in t) >= 1:
            return True
    if not idea_clave:
        return bool(concepto_libro)
    t = (texto or "").lower()
    overlap = _palabras_clave(texto) & _palabras_clave(idea_clave)
    if len(overlap) >= 2:
        return True
    if any(r in t for r in CONCEPTO_RAICES):
        return True
    return any(w in _palabras_clave(idea_clave) for w in _palabras_clave(texto) if len(w) >= 6)


def kpi_asignado_ok(texto: str, kpi_asignado: str) -> bool:
    if not kpi_asignado:
        return True
    return kpi_presente(texto, [kpi_asignado])


def verbos_apertura_repetidos(filas: list[ActionPlanRow], *, max_igual: int = 2) -> list[str]:
    """Temas cuyo verbo inicial se repite más de max_igual veces en el plan."""
    por_verbo: dict[str, list[str]] = {}
    for row in filas:
        pasos = pasos_accion(row.accion_concreta)
        if not pasos or not pasos[0].split():
            continue
        verb = pasos[0].split()[0].lower()
        por_verbo.setdefault(verb, []).append(row.tema)
    repetidos: list[str] = []
    for temas in por_verbo.values():
        if len(temas) > max_igual:
            repetidos.extend(temas[max_igual:])
    return repetidos


def _ctx_por_tema(semanas_ctx: list[dict] | None) -> dict[str, dict]:
    return {c["tema"]: c for c in (semanas_ctx or []) if c.get("tema")}


def validate_action_plan(
    plan: ActionPlan,
    *,
    kpis: list[str] | None = None,
    prohibido: list[str] | None = None,
    semanas_ctx: list[dict] | None = None,
) -> ActionPlanQCResult:
    issues: list[ActionPlanIssue] = []
    kpis = kpis or []
    prohibido = prohibido or []
    ctx_map = _ctx_por_tema(semanas_ctx)

    repetidas = set(filas_repetitivas(plan.filas))
    verbos_rep = set(verbos_apertura_repetidos(plan.filas))
    filas_con_kpi = sum(1 for f in plan.filas if kpi_presente(f.accion_concreta, kpis))

    for row in plan.filas:
        if accion_truncada(row.accion_concreta):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Editor de integridad",
                    row.tema,
                    "Acción truncada o sin cierre de oración.",
                )
            )
        elif accion_muy_corta(row.accion_concreta):
            issues.append(
                ActionPlanIssue(
                    "warning",
                    "Editor de integridad",
                    row.tema,
                    f"Acción muy corta (< {MIN_ACCION_WORDS} palabras).",
                )
            )
        elif accion_muy_larga(row.accion_concreta):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Sintetizador práctico",
                    row.tema,
                    f"Acción muy larga (máx. {MAX_ACCION_WORDS} palabras).",
                )
            )

        if not formato_practico_ok(row.accion_concreta):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Sintetizador práctico",
                    row.tema,
                    "Usa 2-3 pasos separados por « · ».",
                )
            )

        if tiene_cifras_inventadas(row.accion_concreta):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Validador de cifras",
                    row.tema,
                    "Contiene cifras o suposiciones inventadas.",
                )
            )

        if row.tema in repetidas:
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Curador de diversidad",
                    row.tema,
                    "Patrón narrativo repetido respecto a otras semanas.",
                )
            )

        if row.tema in verbos_rep:
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Curador de diversidad",
                    row.tema,
                    "Verbo de apertura repetido en demasiadas semanas.",
                )
            )

        ctx = ctx_map.get(row.tema, {})
        escenario = str(getattr(row, "escenario", "") or ctx.get("escenario", ""))
        if escenario and not escenario_presente(row.accion_concreta, escenario):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Anclador de escenario",
                    row.tema,
                    f"La acción no menciona el escenario: {escenario}.",
                )
            )

        idea = str(ctx.get("idea_clave", ""))
        concepto = str(getattr(row, "concepto_libro", "") or ctx.get("concepto_libro", ""))
        if (idea or concepto) and not concepto_anclado(
            row.accion_concreta, idea, concepto
        ):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Anclador de libro",
                    row.tema,
                    "No ancla la acción al concepto del capítulo.",
                )
            )

        kpi_asignado = str(getattr(row, "kpi_asignado", "") or ctx.get("kpi_asignado", ""))
        if kpi_asignado and not kpi_asignado_ok(row.accion_concreta, kpi_asignado):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Anclador de KPIs",
                    row.tema,
                    f"Debe usar el KPI asignado: {kpi_asignado}.",
                )
            )

        fuera = terminos_fuera_rol(row.accion_concreta, prohibido)
        if fuera:
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Guardián de rol",
                    row.tema,
                    f"Lenguaje fuera del rol: {', '.join(fuera[:3])}.",
                )
            )

        if kpis and not kpi_presente(row.accion_concreta, kpis):
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Anclador de KPIs",
                    row.tema,
                    "No menciona ningún KPI del rol.",
                )
            )
        elif kpis and not kpi_medible_ok(row.accion_concreta, kpis):
            ultimo = ultimo_paso_kpi(row.accion_concreta)
            if kpi_es_vago(ultimo):
                msg = "KPI vago o sin formato Registra:/Mide:."
            else:
                msg = "KPI del rol sin unidad medible (cuántos, minutos, escala, antes/después)."
            issues.append(
                ActionPlanIssue(
                    "error",
                    "Anclador de KPIs",
                    row.tema,
                    msg,
                )
            )

    if kpis and filas_con_kpi < max(1, len(plan.filas) // 2):
        issues.append(
            ActionPlanIssue(
                "warning",
                "Anclador de KPIs",
                "",
                f"Solo {filas_con_kpi}/{len(plan.filas)} filas anclan KPIs del rol.",
            )
        )

    errores = sum(1 for i in issues if i.severity == "error")
    return ActionPlanQCResult(passed=errores == 0, issues=issues)

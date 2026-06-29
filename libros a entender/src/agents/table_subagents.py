"""Sub-agentes especializados para generar cada celda de la tarjeta editorial."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.rol_usuario import RolProfile

VOZ_BLOCK = """VOZ: frases cortas, segunda persona directa (tú, tu, tus), sin rodeos,
sin palabras en inglés, sin tecnicismos. Preguntas que abren. Tensión entre caos y claridad.
Sin frases de autoayuda genérica. Sin LinkedIn. Prohibido yo/mi/me (salvo cita literal del PDF)."""

LECTOR_BLOCK = """LECTOR: trabaja en su oficio, quiere avanzar pero siente que le falta foco.
No tiene tiempo para libros completos. Necesita claridad aplicable a su rol, no más información."""

PROHIBIDOS = """NUNCA USAR:
- "pauso y analizo qué factores influyen"
- Frases de autoayuda vacía
- Palabras en inglés"""

_CONTEXTO_EJEMPLO_PALABRAS = (
    "resumen",
    "resúmenes",
    "contenido",
    "vídeo",
    "video",
    "suscriptor",
    "audiencia",
    "creador",
    "libros",
    "hilos",
    "redes",
    "métricas",
    "cafetería",
    "restaurante",
    "cerámica",
    "diseño",
    "agencia",
    "tienda",
    "plantas",
)


def extract_protagonist(text: str) -> str | None:
    """Primer nombre propio al inicio del ejemplo (p. ej. «Daniela tenía...»)."""
    match = re.match(r"^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\b", (text or "").strip())
    return match.group(1) if match else None


def collect_used_protagonists(ejemplos: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for ejemplo in ejemplos:
        name = extract_protagonist(ejemplo)
        if name and name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def collect_used_contexts(ejemplos: list[str]) -> list[str]:
    found: list[str] = []
    blob = " ".join(ejemplos).lower()
    for word in _CONTEXTO_EJEMPLO_PALABRAS:
        if word in blob and word not in found:
            found.append(word)
    return found


def ejemplo_reuses_protagonist(text: str, ejemplos_anteriores: list[str]) -> bool:
    name = extract_protagonist(text)
    if not name:
        return False
    return name in collect_used_protagonists(ejemplos_anteriores)


APLICACION_YO_PATTERNS = (
    r"\besta semana reviso\b",
    r"\besta semana identifico\b",
    r"\besta semana marco\b",
    r"\byo reviso\b",
    r"\byo priorizo\b",
    r"\bme concentro\b",
    r"\bdejo de\b.*\bmi ",
    r"\binvierto mi\b",
    r"\bmi energía\b",
    r"\bmi agenda\b",
    r"\bmi lista\b",
)


def aplicacion_en_primera_persona(text: str) -> bool:
    """Detecta aplicación en «yo» (debe ser imperativo en «tú»)."""
    t = (text or "").lower()
    return any(re.search(p, t) for p in APLICACION_YO_PATTERNS)


def build_ejemplo_dedup_block(ejemplos_anteriores: list[str]) -> str:
    if not ejemplos_anteriores:
        return ""

    from src.table_validation import build_scenario_dedup_hint

    nombres = collect_used_protagonists(ejemplos_anteriores)
    contextos = collect_used_contexts(ejemplos_anteriores)
    lines = [
        "\nREGLAS DE NO REPETICIÓN (obligatorio):",
        "- Cada ejemplo debe ser una persona, oficio y escena distintos.",
        "- No reutilices la misma estructura narrativa (midió → descubrió → dejó → ganó).",
        "- Varía las cifras del ejemplo: no repitas «cinco de treinta» ni patrones similares.",
    ]
    scenario_hint = build_scenario_dedup_hint(ejemplos_anteriores)
    if scenario_hint:
        lines.append(scenario_hint)
    if nombres:
        lines.append(
            "- Nombres PROHIBIDOS (ya usados): "
            + ", ".join(nombres)
            + ". Inventa un nombre nuevo."
        )
    if contextos:
        lines.append(
            "- Contextos ya usados (elige otro sector): "
            + ", ".join(contextos[:12])
            + "."
        )
    lines.append(
        "- Evita repetir creadores de contenido, resúmenes de libros o métricas "
        "si ya aparecieron en ejemplos anteriores."
    )
    return "\n".join(lines) + "\n"


@dataclass
class TableGenerationContext:
    libro_nombre: str
    tema: str
    texto: str
    extra_block: str
    temas_anteriores: list[str] = field(default_factory=list)
    ejemplos_anteriores: list[str] = field(default_factory=list)
    contexto_usuario: dict | None = None
    rol_perfil: "RolProfile | None" = None
    idea_clave: str = ""
    ejemplo_practico: str = ""


def _rol_prompt_block(ctx: TableGenerationContext, agent: str) -> str:
    from src.rol_usuario import build_rol_block

    if ctx.rol_perfil:
        return build_rol_block(ctx.rol_perfil, agent=agent) + "\n"
    para_aplicacion = agent in ("idea_clave", "aplicacion")
    return _contexto_usuario_block(ctx.contexto_usuario, para_aplicacion=para_aplicacion)


def _parse_json_field(raw: str, field_name: str) -> str | None:
    matches = list(re.finditer(r"\{[^{}]*\}", raw, re.DOTALL))
    if not matches:
        full_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if full_match:
            matches = [full_match]

    for match in reversed(matches):
        try:
            data = json.loads(match.group())
            if field_name in data:
                return str(data[field_name] or "").strip()
        except json.JSONDecodeError:
            continue
    return None


def _contexto_usuario_block(contexto_usuario: dict | None, *, para_aplicacion: bool) -> str:
    if not contexto_usuario:
        return ""
    audiencia = contexto_usuario.get("audiencia", "") or contexto_usuario.get("ocupacion", "")
    reto = contexto_usuario.get("reto", "")
    intento = contexto_usuario.get("intento_fallido", "")
    partes = []
    if audiencia:
        partes.append(f"- Profesión / contexto del lector objetivo: {audiencia}")
    if reto:
        partes.append(f"- Escenario / reto actual: {reto}")
    if intento:
        partes.append(f"- Lo que intentó sin éxito: {intento}")
    if not partes:
        return ""

    if para_aplicacion:
        uso = (
            "OBLIGATORIO: el plan de acción debe hablarle de «tú» al lector, "
            "usar verbos en imperativo y aplicarse directamente a su profesión "
            "y al escenario descrito arriba. No hables de otra profesión genérica."
        )
    else:
        uso = (
            "OBLIGATORIO: el protagonista del ejemplo debe ser la audiencia indicada "
            "(misma profesión u oficio equivalente en el mismo sector). "
            "No uses directores, coordinadores distritales, fonoaudiólogos ni roles "
            "administrativos lejanos si la audiencia es otra."
        )
    return (
        "\nPerfil del lector (escenario a aplicar):\n"
        + "\n".join(partes)
        + f"\n\n{uso}\n"
    )


class IdeaClaveSubAgent:
    """Sub-agente 1/3: genera la idea clave del tema."""

    field = "idea_clave"

    def run(self, llm, ctx: TableGenerationContext) -> str:
        contexto_bloque = _rol_prompt_block(ctx, "idea_clave")
        prompt = f"""Eres un escritor que genera la IDEA CLAVE de una tarjeta de aprendizaje.
No eres un asistente genérico.

{LECTOR_BLOCK}

{VOZ_BLOCK}
{contexto_bloque}
Libro: {ctx.libro_nombre}
Tema: {ctx.tema}
{ctx.extra_block}
Aprendizaje extraído del libro:
{ctx.texto}

Genera SOLO el campo idea_clave:
- La idea más poderosa del tema. Corta. Directa. Que golpee.
- 2-3 oraciones en SEGUNDA PERSONA (tú, tu, tus): habla directo al lector.
- Específica de «{ctx.tema}», no genérica.
- Prohibido primera persona (yo aprendí, me doy cuenta).

{PROHIBIDOS}
- "Aprendí que la idea central de «{ctx.tema}» es:"

Responde SOLO con JSON válido. Sin texto antes ni después. Sin bloques de código.
{{"idea_clave": "..."}}"""

        raw = llm.call(prompt)
        return _parse_json_field(raw, self.field) or raw.strip()


class EjemploPracticoSubAgent:
    """Sub-agente 2/3: genera el ejemplo práctico del tema."""

    field = "ejemplo_practico"

    def run(self, llm, ctx: TableGenerationContext, *, retry_hint: str = "") -> str:
        temas_prev = (
            "\n".join(f"- {t}" for t in ctx.temas_anteriores)
            if ctx.temas_anteriores
            else "Ninguno aún"
        )
        ejemplos_prev = (
            "\n".join(f"- {e}" for e in ctx.ejemplos_anteriores)
            if ctx.ejemplos_anteriores
            else "Ninguno aún"
        )
        dedup_block = build_ejemplo_dedup_block(ctx.ejemplos_anteriores)
        retry_block = f"\n{retry_hint}\n" if retry_hint else ""
        idea_block = (
            f"\nIdea clave ya generada para este tema:\n{ctx.idea_clave}\n"
            if ctx.idea_clave
            else ""
        )
        contexto_bloque = _rol_prompt_block(ctx, "ejemplo")

        prompt = f"""Eres un escritor que genera el EJEMPLO PRÁCTICO de una tarjeta de aprendizaje.
No eres un asistente genérico.

{LECTOR_BLOCK}

VOZ: situación real y concreta. Segunda persona (tú). Narrado directo al lector.
Sin palabras en inglés. Sin tecnicismos. Prohibido yo/mi/me.

Libro: {ctx.libro_nombre}
Tema: {ctx.tema}
{ctx.extra_block}
Temas ya generados en este libro:
{temas_prev}

Ejemplos ya usados en este libro (NO repetir escena, nombre, oficio ni contexto):
{ejemplos_prev}
{dedup_block}{retry_block}{idea_block}{contexto_bloque}
Aprendizaje extraído del libro:
{ctx.texto}

Genera SOLO el campo ejemplo_practico:
- Escena concreta en el trabajo del lector (su aula, gabinete, casos).
- 2-4 oraciones en SEGUNDA PERSONA (tú revisas, descubres, priorizas…).
- DIFERENTE a todos los ejemplos anteriores del libro.
- Ilustra la idea clave sin repetirla textualmente.
- Ancla al perfil del lector objetivo (arriba).

{PROHIBIDOS}

Responde SOLO con JSON válido. Sin texto antes ni después. Sin bloques de código.
{{"ejemplo_practico": "..."}}"""

        raw = llm.call(prompt)
        return _parse_json_field(raw, self.field) or raw.strip()


class AplicacionVidaRealSubAgent:
    """Sub-agente 3/3: genera la aplicación en la vida real del tema."""

    field = "aplicacion_vida_real"

    def run(self, llm, ctx: TableGenerationContext, *, retry_hint: str = "") -> str:
        idea_block = (
            f"\nIdea clave ya generada:\n{ctx.idea_clave}\n"
            if ctx.idea_clave
            else ""
        )
        ejemplo_block = (
            f"\nEjemplo práctico ya generado (mismo escenario, no lo copies):\n{ctx.ejemplo_practico}\n"
            if ctx.ejemplo_practico
            else ""
        )
        contexto_bloque = _rol_prompt_block(ctx, "aplicacion")
        retry_block = f"\n{retry_hint}\n" if retry_hint else ""

        prompt = f"""Eres un escritor que genera la APLICACIÓN EN LA VIDA REAL de una tarjeta.
No eres un asistente genérico.

{LECTOR_BLOCK}

Libro: {ctx.libro_nombre}
Tema / escenario del aprendizaje: {ctx.tema}
{ctx.extra_block}
{idea_block}{ejemplo_block}
Aprendizaje extraído del libro:
{ctx.texto}
{contexto_bloque}{retry_block}
Genera SOLO el campo aplicacion_vida_real:
- Un plan de acción directo, imperativo y en segunda persona (hablándole de «tú» al lector).
- 2-4 instrucciones concretas para ESTA semana (verbos en imperativo: «Revisa…», «Marca…», «Prioriza…»).
- OBLIGATORIO: enfocado en su profesión y en el escenario del tema «{ctx.tema}».
- Si hay perfil del lector arriba, ancla cada acción a su oficio y reto real.
- Prohibido usar primera persona (yo, mi, me, esta semana reviso…).
- Sin vaguedad ni autoayuda genérica.

{PROHIBIDOS}
- "Aplico «{ctx.tema}» en mi vida revisando mis decisiones diarias"
- "Esta semana reviso…" / "Identifico…" en primera persona

Responde SOLO con JSON válido. Sin texto antes ni después. Sin bloques de código.
{{"aplicacion_vida_real": "..."}}"""

        raw = llm.call(prompt)
        return _parse_json_field(raw, self.field) or raw.strip()

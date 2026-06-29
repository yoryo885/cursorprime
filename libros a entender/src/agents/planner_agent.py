"""Agente planificador: convierte un pedido en lenguaje natural en un plan ejecutable."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from src.config import RESUMENES_DIR, VOZ_NOMBRE
from src.output_paths import ensure_book_dirs, meta_dir


PLAN_FILENAME = "plan.json"


@dataclass
class BookPlan:
    """Plan editorial generado antes de ejecutar el pipeline."""

    brief: str
    libro_nombre: str
    libro_slug: str
    pdf_path: str
    temas: list[str]
    audiencia: str
    contexto_usuario: dict[str, str]
    pasos: list[str]
    instrucciones_tablas: dict[str, str]
    voz_lector: str = VOZ_NOMBRE
    notas: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BookPlan:
        return cls(
            brief=str(data.get("brief", "")),
            libro_nombre=str(data.get("libro_nombre", "")),
            libro_slug=str(data.get("libro_slug", "")),
            pdf_path=str(data.get("pdf_path", "")),
            temas=[str(t) for t in data.get("temas", []) if t],
            audiencia=str(data.get("audiencia", "")),
            contexto_usuario={
                k: str(data.get("contexto_usuario", {}).get(k, "") or "")
                for k in ("ocupacion", "reto", "intento_fallido")
            },
            pasos=[str(p) for p in data.get("pasos", []) if p],
            instrucciones_tablas={
                k: str(data.get("instrucciones_tablas", {}).get(k, "") or "")
                for k in ("idea_clave", "ejemplo_practico", "aplicacion_vida_real")
            },
            voz_lector=str(data.get("voz_lector", VOZ_NOMBRE)),
            notas=str(data.get("notas", "")),
        )


class PlannerAgent:
    """
    Organiza un pedido del usuario (libro + audiencia/profesión + objetivo)
    en temas, contexto del lector y secuencia de pasos del pipeline.
    """

    PASOS_DEFAULT = [
        "1. Definir ROL_USUARIO: léxico, KPIs y metodología del oficio (RolUsuarioAgent)",
        "2. Resumir cada tema desde el PDF (Subagent + QualityScorer)",
        "3. Intro general: para quién está hecho el resumen (AudienceIntroAgent)",
        "4. Generar tablas: Idea clave → Ejemplo práctico → Aplicación (3 sub-agentes)",
        "5. Mapa conceptual",
        "6. Plan de acción semanal (ActionPlanAgent: redactor → editor → diversidad → rol → KPIs → QC)",
        "7. Ensamblar PDF editorial (Playwright)",
        "8. Control de calidad final: tablas + PDF (FinalQCAgent)",
    ]

    def __init__(self, llm):
        self.llm = llm

    def run(
        self,
        brief: str,
        *,
        libro: str = "",
        pdf_path: str | Path = "",
        slug: str = "",
        profesion: str = "",
        temas: Optional[list[str]] = None,
    ) -> BookPlan:
        brief = (brief or "").strip()
        if not brief and not libro:
            raise ValueError("Indica qué quieres crear (brief) o al menos el libro.")

        if not brief:
            brief = f"Resumen del libro «{libro}»"
            if profesion:
                brief += f" dedicado a {profesion}"

        prompt = self._build_prompt(
            brief=brief,
            libro=libro,
            profesion=profesion,
            temas=temas or [],
        )
        raw = self.llm.call(prompt)
        plan = self._parse(raw, brief=brief)

        if libro and not plan.libro_nombre:
            plan.libro_nombre = libro
        if profesion and not plan.audiencia:
            plan.audiencia = profesion
        if temas:
            plan.temas = temas
        if slug:
            plan.libro_slug = slug
        if pdf_path:
            plan.pdf_path = str(Path(pdf_path).resolve())

        plan = self._normalize(plan, fallback_libro=libro, fallback_profesion=profesion)
        return plan

    def save(self, plan: BookPlan, output_dir: Path | None = None) -> Path:
        from src.config import AUTOR_OCUPACION

        output_dir = Path(output_dir or RESUMENES_DIR / plan.libro_slug)
        ensure_book_dirs(output_dir)

        plan_path = plan_path_for(output_dir)
        plan_path.write_text(
            json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        ctx = plan.contexto_usuario
        audiencia = plan.audiencia or ctx.get("audiencia", "") or ctx.get("ocupacion", "")
        if audiencia == AUTOR_OCUPACION:
            audiencia = plan.audiencia
        contexto_path = output_dir / "contexto_usuario.json"
        contexto_path.write_text(
            json.dumps(
                {
                    "ocupacion": AUTOR_OCUPACION,
                    "audiencia": audiencia,
                    "reto": ctx.get("reto", ""),
                    "intento_fallido": ctx.get("intento_fallido", ""),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        tablas_hints = output_dir / "meta" / "instrucciones_tablas.json"
        tablas_hints.parent.mkdir(parents=True, exist_ok=True)
        tablas_hints.write_text(
            json.dumps(plan.instrucciones_tablas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        from src.rol_usuario import ensure_rol_perfil

        profile = ensure_rol_perfil(output_dir, llm=self.llm)
        if profile:
            print(
                f"   🎭 ROL_USUARIO activo: «{profile.rol_usuario}» "
                f"({profile.familia_rol})"
            )
        return plan_path

    @staticmethod
    def load(output_dir: Path) -> BookPlan:
        path = plan_path_for(output_dir)
        if not path.exists():
            raise FileNotFoundError(f"No hay plan en {path}")
        return BookPlan.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def _build_prompt(
        self,
        *,
        brief: str,
        libro: str,
        profesion: str,
        temas: list[str],
    ) -> str:
        temas_block = (
            "\n".join(f"- {t}" for t in temas)
            if temas
            else "Inferir 8-12 temas coherentes con el libro y la audiencia."
        )
        profesion_block = profesion or "Inferir del brief si el usuario la menciona."

        return f"""Eres el AGENTE PLANIFICADOR de un sistema que crea resúmenes PDF editoriales.

Tu trabajo NO es escribir el resumen. Organizas QUÉ se va a crear y PARA QUIÉN.

Pedido del usuario:
«{brief}»

Datos opcionales:
- Libro sugerido: {libro or "no indicado"}
- Profesión / audiencia sugerida: {profesion_block}
- Temas indicados por el usuario:
{temas_block}

Genera un plan JSON con EXACTAMENTE estas claves:

- libro_nombre: título del libro (string)
- libro_slug: identificador corto en snake_case, máx 30 chars (string)
- audiencia: a quién va dirigido, ej. «soldador», «psicopedagoga en escuela» (string)
- temas: lista de 8-12 temas a resumir, en español, concretos (array de strings)
- contexto_usuario: objeto con:
    - ocupacion: profesión u oficio del lector objetivo
    - reto: su mayor problema laboral relacionado con el libro
    - intento_fallido: qué hacía antes sin éxito
- instrucciones_tablas: objeto con guías breves para:
    - idea_clave: tono de la idea (1 frase)
    - ejemplo_practico: qué tipo de escenas usar (tercera persona, oficios variados)
    - aplicacion_vida_real: plan imperativo en «tú», anclado a la profesión
- pasos: orden de ejecución del pipeline (array de strings, 4-6 pasos)
- notas: resumen ejecutivo de 2-3 frases para el usuario

Reglas:
- Si el pedido menciona una profesión (soldador, maestro, etc.), TODA la personalización
  debe girar en torno a esa profesión (ROL_USUARIO: léxico, KPIs y metodología del oficio).
- Los temas deben ser útiles para ESA audiencia, no genéricos.
- aplicacion_vida_real siempre en segunda persona imperativa («tú»), nunca «yo reviso».
- Responde SOLO JSON válido, sin markdown ni texto extra."""

    def _parse(self, text: str, *, brief: str) -> BookPlan:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("El planificador no devolvió JSON válido.")
        data = json.loads(match.group())
        data["brief"] = brief
        return BookPlan.from_dict(data)

    def _normalize(
        self,
        plan: BookPlan,
        *,
        fallback_libro: str,
        fallback_profesion: str,
    ) -> BookPlan:
        if not plan.libro_nombre:
            plan.libro_nombre = fallback_libro or "Libro sin título"
        if not plan.libro_slug:
            plan.libro_slug = _slugify(plan.libro_nombre)
        if not plan.pdf_path:
            plan.pdf_path = str(_resolve_pdf(plan.libro_nombre))
        if fallback_profesion and not plan.contexto_usuario.get("ocupacion"):
            plan.contexto_usuario["ocupacion"] = fallback_profesion
        if fallback_profesion and not plan.audiencia:
            plan.audiencia = fallback_profesion
        if not plan.temas:
            plan.temas = ["Tema principal"]
        if not plan.pasos:
            plan.pasos = list(self.PASOS_DEFAULT)
        if not plan.instrucciones_tablas.get("aplicacion_vida_real"):
            prof = plan.contexto_usuario.get("ocupacion") or plan.audiencia
            plan.instrucciones_tablas["aplicacion_vida_real"] = (
                f"Plan imperativo en «tú», anclado a {prof or 'su profesión'}."
            )
        return plan


def plan_path_for(output_dir: Path) -> Path:
    return meta_dir(output_dir) / PLAN_FILENAME


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:30] or "libro"


def _resolve_pdf(libro: str) -> Path:
    directa = Path(libro)
    if directa.exists():
        return directa.resolve()
    en_carpeta = Path("libros") / f"{libro}.pdf"
    if en_carpeta.exists():
        return en_carpeta.resolve()
    return directa

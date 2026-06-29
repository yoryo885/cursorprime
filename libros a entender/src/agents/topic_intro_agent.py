"""Genera una introducción por tema anclada al oficio/audiencia del lector."""
from __future__ import annotations

from pathlib import Path

from src.models import TopicResult
from src.topic_intros_store import apply_topic_intros, load_topic_intros, save_topic_intros


class TopicIntroAgent:
    """Conecta cada tema del libro con el trabajo concreto del lector objetivo."""

    def __init__(self, llm):
        self.llm = llm

    def run(
        self,
        resultados: list[TopicResult],
        output_dir: Path,
        *,
        libro_nombre: str,
        audiencia: str = "",
        contexto_usuario: dict | None = None,
        force: bool = False,
    ) -> dict[str, str]:
        output_dir = Path(output_dir)
        existentes, audiencia_guardada = load_topic_intros(output_dir)
        audiencia = audiencia or audiencia_guardada or _audiencia_desde_contexto(contexto_usuario)

        if not audiencia:
            print("   ⏭️  Intros por tema: sin audiencia/oficio definido")
            apply_topic_intros(resultados, existentes)
            return existentes

        if existentes and not force and _cubre_temas(existentes, resultados):
            print(f"   ⏭️  Intros por tema: reutilizando {len(existentes)} existentes")
            apply_topic_intros(resultados, existentes)
            return existentes

        print(f"   📌 Agente Intros tema: anclando a «{audiencia}»...")
        intros: dict[str, str] = dict(existentes)
        for resultado in resultados:
            if resultado.fallo:
                continue
            if not force and resultado.tema in intros and intros[resultado.tema].strip():
                continue
            print(f"      → Intro: '{resultado.tema}'...")
            intros[resultado.tema] = self._generar(
                tema=resultado.tema,
                libro_nombre=libro_nombre,
                audiencia=audiencia,
                contexto_usuario=contexto_usuario or {},
                resumen=(resultado.resumen_voz or resultado.resumen)[:600],
            )

        save_topic_intros(output_dir, intros, audiencia=audiencia)
        apply_topic_intros(resultados, intros)
        return intros

    def _generar(
        self,
        *,
        tema: str,
        libro_nombre: str,
        audiencia: str,
        contexto_usuario: dict,
        resumen: str,
    ) -> str:
        reto = contexto_usuario.get("reto", "")
        intento = contexto_usuario.get("intento_fallido", "")
        prompt = f"""Eres un editor que escribe la INTRODUCCIÓN de un tema en un resumen PDF.

Libro: «{libro_nombre}»
Tema del libro: «{tema}»
Lector objetivo: {audiencia}
Reto laboral: {reto or "no indicado"}
Lo que intentó sin éxito: {intento or "no indicado"}

Contexto del resumen de este tema (referencia, no copies):
{resumen[:500]}

Escribe 2-3 oraciones CORTAS (máximo 280 caracteres en total) que:
- Hablen al lector en segunda persona («tú», «tu», «te») o como {audiencia}.
- Expliquen POR QUÉ este tema importa en SU oficio y contexto diario.
- Conecten el concepto del libro con una situación real de su trabajo (aula, gabinete, taller, etc.).
- No resuman el libro ni repitan la idea clave del tema.
- No usen primera persona del autor (yo leí, aprendí).
- Sin palabras en inglés. Sin tono de autoayuda genérica.

Ejemplo de tono (psicopedagoga):
«En el gabinete te llegan decenas de casos y todos parecen urgentes. Este tema te ayuda a ver cuáles concentran la mayor parte de tu impacto real, para dejar de agotarte repartiendo la misma energía.»

Responde SOLO con el texto de la introducción. Sin comillas. Sin título."""

        raw = self.llm.call(prompt)
        return raw.strip().strip('"').strip("«»")


def _audiencia_desde_contexto(contexto: dict | None) -> str:
    if not contexto:
        return ""
    return str(contexto.get("ocupacion", "") or contexto.get("audiencia", "") or "").strip()


def _cubre_temas(intros: dict[str, str], resultados: list[TopicResult]) -> bool:
    temas = [r.tema for r in resultados if not r.fallo]
    return bool(temas) and all(intros.get(t, "").strip() for t in temas)


def resolve_audiencia(output_dir: Path, contexto_usuario: dict | None = None) -> str:
    import json

    from src.agents.planner_agent import BookPlan, plan_path_for

    try:
        plan = BookPlan.from_dict(
            json.loads(plan_path_for(output_dir).read_text(encoding="utf-8"))
        )
        aud = plan.audiencia or plan.contexto_usuario.get("ocupacion", "")
        if aud:
            return aud
    except Exception:
        pass
    return _audiencia_desde_contexto(contexto_usuario)

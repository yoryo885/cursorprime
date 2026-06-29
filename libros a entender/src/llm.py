import json
import re
import threading
import time
from typing import Optional, Union

from anthropic import Anthropic, RateLimitError

from src.config import (
    CLAUDE_MODEL,
    LLM_MAX_RETRIES,
    LLM_RETRY_BUFFER_SECS,
    MAX_TOKENS_SUMMARY,
)


class LLMClient:
    """Cliente para la API de Anthropic (Claude)."""

    _lock = threading.Lock()

    def __init__(self, api_key: str, model: str = CLAUDE_MODEL):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def analyze_topic(
        self,
        tema: str,
        chunks: list[str],
        libro_nombre: str = "",
        extra_instructions: Optional[Union[str, list[str]]] = None,
        intento: int = 1,
    ) -> tuple[list[str], str]:
        """Identifica fragmentos relevantes y genera resumen con Claude."""
        if not chunks:
            return [], (
                f"No hay contenido disponible del PDF para analizar el tema '{tema}'."
            )

        chunks_text = self._format_chunks(chunks)
        prompt = self._build_prompt(
            tema, chunks_text, libro_nombre, extra_instructions, intento
        )
        text = self._call_with_retry(prompt)
        return self._parse_response(text)

    def call(self, prompt: str) -> str:
        """Llamada genérica al LLM (para agentes de post-procesamiento)."""
        return self._call_with_retry(prompt)

    def generate_agent_improvements(
        self,
        errores: list[dict],
        stats: dict,
        instrucciones_actuales: dict,
        libro_nombre: str,
    ) -> dict:
        """Genera mejoras globales y por agente para logs/mejoras.json."""
        prompt = f"""Eres el agente de aprendizaje de un sistema multi-agente que resume libros.

Libro procesado: "{libro_nombre}"
Estadísticas: {json.dumps(stats, ensure_ascii=False)}
Errores detectados: {json.dumps(errores, ensure_ascii=False, indent=2)}
Prompts actuales por agente: {json.dumps(instrucciones_actuales, ensure_ascii=False, indent=2)}

Analiza errores y resultados. Genera mejoras NUEVAS (sin repetir las existentes) para:
- instrucciones globales de resumen
- prompts específicos de agentes: tablas, mapa, imagenes, pdf

Responde SOLO con JSON:
{{
  "instrucciones": ["mejora global 1", "..."],
  "prompts_agentes": {{
    "tablas": ["..."],
    "mapa": ["..."],
    "imagenes": ["..."],
    "pdf": ["..."]
  }}
}}
Máximo 3 instrucciones por sección."""

        text = self._call_with_retry(prompt)
        return self._parse_agent_improvements(text)

    def _parse_agent_improvements(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group())
            return {
                "instrucciones": [str(i) for i in data.get("instrucciones", []) if i],
                "prompts_agentes": {
                    k: [str(p) for p in v if p]
                    for k, v in data.get("prompts_agentes", {}).items()
                    if isinstance(v, list)
                },
            }
        except json.JSONDecodeError:
            return {}

    def correct_topic_text(
        self,
        tema: str,
        resumen: str,
        fragmentos: list[str],
    ) -> tuple[str, list[str]]:
        """Corrige ortografía, idioma y coherencia del texto generado."""
        fragmentos_text = "\n".join(f"- {f}" for f in fragmentos) or "(ninguno)"

        prompt = f"""Eres un corrector editorial experto en español de España/Latinoamérica.

Revisa y corrige el siguiente texto generado por IA sobre el tema "{tema}".

OBLIGATORIO:
1. Corregir TODOS los errores ortográficos y gramaticales
2. Eliminar o traducir TODA palabra en inglés (ej: "Understanding" → "comprensión", "function" → "función")
3. Reescribir frases sin sentido, incompletas o mal construidas
4. Mantener el significado, ideas y citas del libro
5. El resultado debe estar 100% en español correcto y fluido

TEXTO A CORREGIR:

## Resumen
{resumen}

## Fragmentos
{fragmentos_text}

Responde SOLO con JSON válido (sin markdown):
{{"resumen": "texto corregido del resumen", "fragmentos": ["fragmento 1 corregido", "fragmento 2 corregido"]}}"""

        text = self._call_with_retry(prompt)
        return self._parse_correction(text, resumen, fragmentos)

    def _parse_correction(
        self,
        text: str,
        resumen_original: str,
        fragmentos_originales: list[str],
    ) -> tuple[str, list[str]]:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return resumen_original, fragmentos_originales
        try:
            data = json.loads(match.group())
            resumen = str(data.get("resumen", resumen_original)).strip()
            fragmentos_raw = data.get("fragmentos", fragmentos_originales)
            if isinstance(fragmentos_raw, list):
                fragmentos = [str(f).strip() for f in fragmentos_raw if str(f).strip()]
            else:
                fragmentos = fragmentos_originales
            if resumen:
                return resumen, fragmentos or fragmentos_originales
        except (json.JSONDecodeError, TypeError):
            pass
        return resumen_original, fragmentos_originales

    def generate_improvements(
        self,
        errores: list[dict],
        instrucciones_actuales: list[str],
        libro_nombre: str,
    ) -> list[str]:
        """Analiza errores y propone mejoras de instrucciones para futuros libros."""
        errores_text = json.dumps(errores, ensure_ascii=False, indent=2)
        actuales = "\n".join(f"- {i}" for i in instrucciones_actuales) or "(ninguna)"

        prompt = f"""Eres el agente principal de un sistema que resume libros PDF por temas.

Acabas de procesar el libro "{libro_nombre}" y detectaste estos errores o problemas de calidad:

{errores_text}

Instrucciones de mejora que ya tienes acumuladas:
{actuales}

Analiza los errores y genera NUEVAS instrucciones concretas para que los subagentes
produzcan mejores resúmenes en el PRÓXIMO libro. Las instrucciones deben ser:
- Específicas y accionables
- En español
- Sin repetir las que ya existen
- Máximo 5 instrucciones nuevas

Responde SOLO con un JSON array de strings, ejemplo:
["Escribe todo en español sin mezclar palabras en inglés.", "Incluye al menos 3 fragmentos citados del libro."]"""

        text = self._call_with_retry(prompt)
        return self._parse_json_list(text)

    def _call_with_retry(self, prompt: str) -> str:
        last_error = None
        for _ in range(LLM_MAX_RETRIES):
            try:
                with self._lock:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=MAX_TOKENS_SUMMARY,
                        messages=[{"role": "user", "content": prompt}],
                    )
                content = response.content[0].text
                time.sleep(1)
                return content
            except RateLimitError as err:
                last_error = err
                wait = self._parse_retry_after(str(err))
                print(f"      ⏳ Rate limit, esperando {wait:.0f}s...")
                time.sleep(wait)
        raise last_error  # type: ignore[misc]

    def _parse_retry_after(self, error_msg: str) -> float:
        match = re.search(r"retry.after[:\s]+(\d+)", error_msg, re.I)
        if match:
            return int(match.group(1)) + LLM_RETRY_BUFFER_SECS
        match = re.search(r"try again in ([\d.]+)s", error_msg)
        if match:
            return float(match.group(1)) + LLM_RETRY_BUFFER_SECS
        return 30 + LLM_RETRY_BUFFER_SECS

    def _parse_json_list(self, text: str) -> list[str]:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return [str(item) for item in data if item]
        except json.JSONDecodeError:
            pass
        return []

    def _format_chunks(self, chunks: list[str]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(f"--- Fragmento {i} ---\n{chunk}")
        return "\n\n".join(parts)

    def _build_prompt(
        self,
        tema: str,
        chunks_text: str,
        libro: str,
        extra_instructions: Optional[Union[str, list[str]]] = None,
        intento: int = 1,
    ) -> str:
        mejoras = ""
        if extra_instructions:
            if isinstance(extra_instructions, str):
                mejoras = extra_instructions if extra_instructions.startswith("\n") else f"\n{extra_instructions}\n"
            else:
                items = "\n".join(f"- {inst}" for inst in extra_instructions)
                mejoras = f"""
**Instrucciones de mejora aprendidas (aplica todas):**
{items}

"""
        retry_note = ""
        if intento > 1:
            retry_note = (
                "\n**Este es un reintento:** mejora longitud, segunda persona (tú), "
                "voz directa y uso de fragmentos.\n"
            )

        return f"""Eres un subagente que extrae ideas de un PDF y las convierte en aprendizaje aplicable.

**Libro:** {libro or "PDF"}
**Tema a investigar:** {tema}
{mejoras}{retry_note}
Fragmentos extraídos del PDF (única fuente permitida):

{chunks_text}

---

VOZ Y ESTILO — aplica en cada línea del resumen:
- Frases cortas. Máximo dos líneas por idea.
- Segunda persona directa al lector: "Notarás que...", "Descubrirás que...", "Tu trabajo..."
- Sin tecnicismos, sin palabras en inglés, sin frases de autoayuda genérica
- Tensión entre el caos de antes y la claridad que da esta idea
- Usa preguntas que abren: "¿Cuánto tiempo llevas haciendo esto sin verlo?", "¿Qué pasaría si...?"
- El lector siente que la respuesta está en él, no en el libro
- Sin LinkedIn. Sin coach de vida. Sin "potencial".
- PROHIBIDO primera persona (yo, me, mi, aprendí, entiendo, noto).

REGLAS OBLIGATORIAS:
- Usa SOLO información presente en los fragmentos del PDF
- Todo el texto va en SEGUNDA PERSONA (tú, tu, tus, te, contigo)
- NO menciones al autor, el título del libro ni frases como "el autor dice", "según el libro"
- Parafrasea las ideas del PDF como consejo directo al lector, no como reseña externa
- Español correcto y natural

Responde EXACTAMENTE con este formato:

## Fragmentos relevantes
- [Idea del PDF parafraseada hacia el lector: "Verás que...", "Notarás que..."]
- [Otra idea relevante si existe]
(Usa "-" por cada fragmento. Si ningún fragmento es relevante: - No encontré información relevante en el PDF.)

## Resumen
[3-6 párrafos en SEGUNDA PERSONA (tú) sintetizando lo que extrajiste del PDF sobre "{tema}".
Voz directa, frases cortas, tensión entre el antes y el después de entender esto.
Como guía personal para el lector — no reseña, no resumen académico.]"""

    def _parse_response(self, text: str) -> tuple[list[str], str]:
        fragmentos_match = re.search(
            r"##\s*Fragmentos relevantes\s*\n(.*?)(?=\n##\s*Resumen|\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        resumen_match = re.search(
            r"##\s*Resumen\s*\n(.*)",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        fragmentos: list[str] = []
        if fragmentos_match:
            bloque = fragmentos_match.group(1).strip()
            for linea in bloque.split("\n"):
                linea = linea.strip()
                if linea.startswith("- "):
                    contenido = linea[2:].strip()
                    if contenido and "no se encontró" not in contenido.lower():
                        fragmentos.append(contenido)

        resumen = resumen_match.group(1).strip() if resumen_match else text.strip()
        return fragmentos, resumen


# Alias retrocompatible
GroqClient = LLMClient

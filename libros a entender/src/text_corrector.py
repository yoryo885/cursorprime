import copy
import json
import re
from pathlib import Path
from typing import Optional

from src.llm import LLMClient
from src.models import TopicResult
from src.text_sanitize import clean_resumen_markdown


class TextCorrector:
    """Corrige ortografía, mezcla de idiomas y frases mal formadas antes del export."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def correct_all(
        self,
        resultados: list[TopicResult],
        *,
        output_dir: Optional[Path] = None,
    ) -> list[TopicResult]:
        rol_block = self._load_rol_block(output_dir)
        corregidos = []
        for resultado in resultados:
            if resultado.fallo or not resultado.resumen.strip():
                corregidos.append(resultado)
                continue

            print(f"      ✏️  Corrigiendo: '{resultado.tema}'...")
            corregido = self._correct_one(resultado, rol_block=rol_block)
            corregidos.append(corregido)

        return corregidos

    @staticmethod
    def _load_rol_block(output_dir: Optional[Path]) -> str:
        if output_dir is None:
            return ""
        from src.rol_usuario import build_rol_block, ensure_rol_perfil

        profile = ensure_rol_perfil(Path(output_dir))
        return build_rol_block(profile, agent="corrector")

    def _correct_one(self, resultado: TopicResult, *, rol_block: str = "") -> TopicResult:
        copia = copy.copy(resultado)
        try:
            prompt = self._build_prompt(
                tema=resultado.tema,
                resumen=resultado.resumen,
                fragmentos=resultado.fragmentos,
                rol_block=rol_block,
            )
            text = self.llm.call(prompt)
            resumen, fragmentos = self._parse_response(
                text, resultado.resumen, resultado.fragmentos
            )
            copia.resumen = resumen
            copia.fragmentos = fragmentos
            copia.calidad_issues = []
        except Exception as err:
            print(f"         ⚠️  Corrección falló: {err}")
        return copia

    def _build_prompt(
        self,
        tema: str,
        resumen: str,
        fragmentos: list[str],
        *,
        rol_block: str = "",
    ) -> str:
        fragmentos_text = "\n".join(f"- {f}" for f in fragmentos) or "(ninguno)"
        rol_section = f"\n{rol_block}\n" if rol_block else ""

        return f"""Eres un corrector editorial experto en español de España/Latinoamérica.

Revisa y corrige el siguiente texto generado por IA sobre el tema "{tema}".
{rol_section}
OBLIGATORIO:
1. Corregir TODOS los errores ortográficos y gramaticales
2. Eliminar o traducir TODA palabra en inglés mezclada con el español
   (ej: "Understanding" → "comprensión", "function" → "función", "Describe" → "describe")
3. Detectar y reescribir frases sin sentido, incompletas, incoherentes o mal construidas
4. Eliminar repeticiones vacías y muletillas que no aporten significado
5. Mantener y reforzar la SEGUNDA PERSONA en todo el texto (tú, tu, tus, te)
6. Eliminar cualquier primera persona (yo, me, mi, aprendí) salvo cita literal del PDF
7. Eliminar referencias al autor o al libro ("el autor", "según el libro", nombres de autores)
8. El resultado debe estar 100% en español correcto, fluido y natural

TEXTO A CORREGIR:

## Resumen
{resumen}

## Fragmentos
{fragmentos_text}

Responde SOLO con JSON válido (sin markdown):
{{"resumen": "texto corregido del resumen", "fragmentos": ["fragmento 1 corregido", "fragmento 2 corregido"]}}"""

    def _parse_response(
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
            resumen = clean_resumen_markdown(str(data.get("resumen", resumen_original)).strip())
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

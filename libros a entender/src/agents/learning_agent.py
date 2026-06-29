import json
from typing import Optional

from src.learning import LearningSystem
from src.llm import LLMClient


class LearningAgent:
    """
    Agente de aprendizaje: analiza errores y resultados del pipeline completo
    y mejora prompts internos de todos los agentes.
    """

    def __init__(self, learning: LearningSystem):
        self.learning = learning

    def run(
        self,
        llm: LLMClient,
        libro_slug: str,
        libro_nombre: str,
        resultados: list,
        tablas_count: int,
        imagenes_count: int,
        pdf_ok: bool,
    ) -> list[str]:
        print("   🧠 Agente Aprendizaje: analizando resultados del pipeline...")
        try:
            session_errors = [
                e for e in self.learning._session_errors
                if e.get("libro_slug") == libro_slug
            ]
            resumen_stats = {
                "temas_total": len(resultados),
                "temas_fallidos": sum(1 for r in resultados if r.fallo),
                "tablas_generadas": tablas_count,
                "imagenes_descargadas": imagenes_count,
                "pdf_generado": pdf_ok,
            }
            nuevas = llm.generate_agent_improvements(
                errores=session_errors,
                stats=resumen_stats,
                instrucciones_actuales=self.learning.load_all_prompts(),
                libro_nombre=libro_nombre,
            )
            if nuevas:
                self.learning.save_agent_improvements(libro_slug, libro_nombre, nuevas)
                print(f"      ✓ {len(nuevas.get('instrucciones', []))} mejoras globales")
                for agente, prompts in nuevas.get("prompts_agentes", {}).items():
                    if prompts:
                        print(f"      ✓ Agente '{agente}': {len(prompts)} prompts")
                return nuevas.get("instrucciones", [])
            print("      ✓ Sin nuevas mejoras necesarias")
            return []
        except Exception as err:
            print(f"      ⚠️  Aprendizaje falló: {err}")
            return []

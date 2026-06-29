"""Agente de aprendizaje: mejora automática de la pipeline de marketing."""
from __future__ import annotations

import json

from src.llm import LLMClient
from src.marketing.learning import MarketingLearningSystem
from src.marketing.models import KDPListing
from src.marketing.quality import MarketingQCReport
from src.marketing.utils import parse_json_response


class MarketingLearningAgent:
    """
    Tras cada listing, analiza QC + historial y propone mejoras
    que se aplican solas en la siguiente ejecución.
    """

    def __init__(self, learning: MarketingLearningSystem):
        self.learning = learning

    def run(
        self,
        llm: LLMClient,
        listing: KDPListing,
        qc: MarketingQCReport,
    ) -> list[str]:
        print("\n🧠 MarketingLearningAgent: analizando listing...")
        try:
            nuevas = self._generar_mejoras(llm, listing, qc)
            if not nuevas:
                print("      ✓ Sin nuevas mejoras necesarias")
                return []

            aplicadas = self.learning.save_improvements(
                pdf_origen=listing.pdf_origen,
                titulo=listing.titulo,
                nuevas=nuevas,
            )
            if aplicadas:
                print(f"      ✓ {len(aplicadas)} mejoras guardadas para próximos listings")
                for m in aplicadas[:5]:
                    print(f"        · {m[:90]}")
                if len(aplicadas) > 5:
                    print(f"        · ... y {len(aplicadas) - 5} más")
            return aplicadas
        except Exception as err:
            print(f"      ⚠️  Aprendizaje marketing falló: {err}")
            return []

    def _generar_mejoras(
        self,
        llm: LLMClient,
        listing: KDPListing,
        qc: MarketingQCReport,
    ) -> dict:
        actuales = self.learning.load_all()
        metricas = self.learning.metricas_recientes(5)

        prompt = f"""Eres el agente de aprendizaje de un sistema multi-agente de marketing Amazon KDP.

LISTING GENERADO:
- Título: {listing.titulo}
- Keywords: {", ".join(listing.keywords)}
- Audiencia: {listing.analisis.audiencia}
- Serie: {listing.serie}

CONTROL DE CALIDAD:
- Score: {qc.score}/10
- Issues: {json.dumps(qc.issues, ensure_ascii=False)}
- Warnings: {json.dumps(qc.warnings, ensure_ascii=False)}

EVENTOS DE ESTA SESIÓN:
{json.dumps(self.learning.session_events(), ensure_ascii=False, indent=2)}

MÉTRICAS AMAZON RECIENTES (si hay):
{json.dumps(metricas, ensure_ascii=False, indent=2)}

MEJORAS YA APLICADAS (no repetir):
{json.dumps(actuales, ensure_ascii=False, indent=2)}

Genera mejoras NUEVAS y accionables para el próximo listing:
- instrucciones_globales: reglas para todos los agentes de marketing
- prompts_agentes.contenido / titulo / descripcion / keywords

Enfócate en: SEO en español MX/ES, cumplir KDP, claridad por rol, evitar palabras prohibidas.
Máximo 2 instrucciones globales y 2 por agente.

Responde SOLO con JSON:
{{
  "instrucciones_globales": ["..."],
  "prompts_agentes": {{
    "contenido": ["..."],
    "titulo": ["..."],
    "descripcion": ["..."],
    "keywords": ["..."]
  }}
}}"""

        raw = llm.call(prompt)
        data = parse_json_response(raw)
        if not data:
            return {}

        prompts = {}
        raw_prompts = data.get("prompts_agentes", {})
        if isinstance(raw_prompts, dict):
            for agente in ("contenido", "titulo", "descripcion", "keywords"):
                vals = raw_prompts.get(agente, [])
                if isinstance(vals, list):
                    prompts[agente] = [str(v) for v in vals if v]

        return {
            "instrucciones_globales": [
                str(i) for i in data.get("instrucciones_globales", []) if i
            ],
            "prompts_agentes": prompts,
        }

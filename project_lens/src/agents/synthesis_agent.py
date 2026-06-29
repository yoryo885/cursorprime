"""Agente 9 — Synthesis / Verdict."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext

AREA_KEYS = ["trend", "market", "competition", "financial", "scalability", "cost_mvp", "risk"]
SCORE_MAP = {
    "trend": lambda d: d.get("metrics", {}).get("trend_score", {}).get("point", 5) * 10,
    "market": lambda d: d.get("metrics", {}).get("demanda_score", {}).get("point", 5) * 10,
    "competition": lambda d: 70 if d.get("extra", {}).get("saturacion") == "baja" else 50 if d.get("extra", {}).get("saturacion") == "media" else 35,
    "financial": lambda d: d.get("metrics", {}).get("margen_neto_pct", {}).get("point", 25),
    "scalability": lambda d: d.get("metrics", {}).get("scalability_score", {}).get("point", 5) * 10,
    "cost_mvp": lambda d: 75 if d.get("extra", {}).get("complejidad") == "baja" else 55 if d.get("extra", {}).get("complejidad") == "media" else 40,
    "risk": lambda d: max(20, 100 - d.get("extra", {}).get("severidad_max", 3) * 15),
}


class SynthesisAgent:
    key = "synthesis"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        tipo = context.get("tipo_negocio", "saas")
        weights_table = ctx.weights.get("tipos", {}).get(tipo) or ctx.weights.get("tipos", {}).get("saas", {})

        por_area = {}
        weighted_sum = 0.0
        weight_sum = 0.0
        confidences = []

        for area in AREA_KEYS:
            path = ctx.paths.get(area)
            if not path or not path.exists():
                continue
            data = load_json(path, {})
            if not data:
                continue
            score_fn = SCORE_MAP.get(area, lambda d: 50)
            point = float(score_fn(data))
            conf = float(data.get("confidence", 0.5))
            w = float(weights_table.get(area, 0.14))
            por_area[area] = {"score": point, "confidence": conf, "weight": w}
            weighted_sum += point * conf * w
            weight_sum += w * conf
            confidences.append(conf)

        score_point = weighted_sum / weight_sum if weight_sum else 50
        score_min = max(0, score_point - 12)
        score_max = min(100, score_point + 12)
        conf_global = sum(confidences) / len(confidences) if confidences else 0.5

        if score_point >= 65 and conf_global >= 0.55:
            veredicto = "viable"
        elif score_point < 40:
            veredicto = "descartar"
        else:
            veredicto = "condicional"

        risk = load_json(ctx.paths.get("risk"), {})
        if risk.get("extra", {}).get("severidad_max", 0) >= 4 and veredicto == "viable":
            veredicto = "condicional"

        data = {
            "agent": "SynthesisAgent",
            "score_global": {"min": round(score_min, 1), "max": round(score_max, 1), "point": round(score_point, 1)},
            "confidence_global": round(conf_global, 2),
            "veredicto": veredicto,
            "veredicto_labels": ["viable", "condicional", "descartar"],
            "por_area": por_area,
            "tipo_negocio": tipo,
            "recomendacion": f"Veredicto {veredicto} — validar hipótesis clave antes de escalar",
            "siguiente_paso": "Ejecutar plan_accion fase 1" if veredicto != "descartar" else "Pivotar o entrevistar 5 clientes",
        }
        save_json(ctx.paths["synthesis"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["synthesis"])])

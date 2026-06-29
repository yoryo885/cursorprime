"""Agente 10 — Planner."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PlannerAgent:
    key = "planner"

    def run(self, ctx: PipelineContext) -> AgentResult:
        verdict = load_json(ctx.paths["synthesis"], {})
        cost = load_json(ctx.paths.get("cost_mvp"), {})
        veredicto = verdict.get("veredicto", "condicional")
        sem = cost.get("metrics", {}).get("semanas", {})
        sem_min, sem_max = sem.get("min", 2), sem.get("max", 8)
        checklist = cost.get("extra", {}).get("checklist_mvp", [])

        if veredicto == "descartar":
            fases = [{
                "id": 1, "nombre": "Validación mínima", "semanas": 1,
                "objetivo": "Confirmar si el problema es real",
                "tareas": [{"id": "1.1", "tarea": "5 entrevistas cliente", "prioridad": "alta"}],
                "criterio_exito": "Al menos 2 confirman dolor",
            }]
        else:
            fases = [
                {
                    "id": 1, "nombre": "Validación", "semanas": max(1, int(sem_min / 2)),
                    "objetivo": "Validar disposición a pagar",
                    "tareas": [{"id": "1.1", "tarea": t, "prioridad": "alta"} for t in checklist[:2]],
                    "criterio_exito": "3 señales de interés",
                },
                {
                    "id": 2, "nombre": "MVP", "semanas": int(sem_min),
                    "objetivo": "MVP testeable",
                    "tareas": [{"id": "2.1", "tarea": t, "prioridad": "media"} for t in checklist[2:4] or ["Prototipo core"]],
                    "criterio_exito": "1 usuario piloto activo",
                },
            ]

        data = {
            "agent": "PlannerAgent",
            "veredicto_base": veredicto,
            "horizonte_semanas": {"min": sem_min, "max": sem_max},
            "fases": fases,
            "hitos": [{"semana": sem_min, "hito": "MVP testeable"}],
            "siguiente_accion_inmediata": verdict.get("siguiente_paso", "Iniciar fase 1"),
        }
        save_json(ctx.paths["planner"], data)
        return AgentResult(ok=True, data=data, artifacts=[str(ctx.paths["planner"])])

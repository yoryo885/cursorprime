"""HookAgent — ganchos de apertura (heurística o LLM si MOCK_LLM=false)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.llm_client import get_llm, llm_activo
from src.types import AgentResult, PipelineContext


def _base_tema(lote: dict, context: dict) -> str:
    guia = lote.get("guia") or {}
    if isinstance(guia, dict) and guia.get("titulo"):
        return str(guia["titulo"])
    return str(context.get("titulo") or lote.get("titulo") or "esta guía")


def _promesa(lote: dict) -> str:
    guia = lote.get("guia") or {}
    if isinstance(guia, dict):
        return str(guia.get("promesa") or guia.get("beneficio") or "")
    return ""


def _mock_hooks(tema: str, promesa: str, ideas: list[str]) -> dict:
    hooks = [
        {"id": 1, "texto": f"Si {tema} te abruma, esto te ordena en minutos.", "angulo": "dolor"},
        {
            "id": 2,
            "texto": f"La mayoría lee PDFs y no aplica nada. Esta guía sí: {promesa}.",
            "angulo": "contraste",
        },
        {
            "id": 3,
            "texto": (
                f"3 ideas de «{tema}» que puedes usar hoy"
                + (f" — empezando por {ideas[0]}" if ideas else "")
                + "."
            ),
            "angulo": "lista",
        },
    ]
    return {"hooks": hooks, "elegido": hooks[0], "confidence": "medium", "modo": "heuristica"}


class HookAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        tema = _base_tema(lote, context)
        promesa = _promesa(lote) or f"claridad práctica sobre {tema}"
        ideas: list[str] = []
        guia = lote.get("guia") or {}
        if isinstance(guia, dict):
            ideas = [str(x) for x in (guia.get("ideas") or guia.get("puntos") or [])[:3]]

        mock = _mock_hooks(tema, promesa, ideas)
        data = mock
        if llm_activo() and not lote.get("hook"):
            system = (
                "Eres copy de Reels/TikTok. Skill hooks-redes: máx 1 frase, sin saludo, "
                "curiosidad o tensión en 3 segundos. JSON: hooks[{id,texto,angulo}], elegido."
            )
            user = f"Tema: {tema}\nPromesa: {promesa}\nIdeas: {ideas}\nGenera 3 hooks y elige uno."
            try:
                data = get_llm().complete_json(system, user, mock_payload=mock)
                data["modo"] = "llm"
                data["confidence"] = data.get("confidence") or "medium"
            except Exception as exc:
                data = {**mock, "modo": "heuristica_fallback", "warning": str(exc)[:120]}

        hooks = data.get("hooks") or mock["hooks"]
        elegido = data.get("elegido") or hooks[0]
        if lote.get("hook"):
            elegido = {"id": 0, "texto": str(lote["hook"]), "angulo": "manual"}
            data["modo"] = "manual"

        payload = {
            "skill": "hooks-redes",
            "tema": tema,
            "hooks": hooks,
            "elegido": elegido,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": data.get("confidence", "medium"),
            "modo": data.get("modo", "heuristica"),
            "nota": "MOCK_LLM=false + ANTHROPIC_API_KEY activa LLM; si no, heurística",
        }
        out = ctx.paths["hooks"]
        save_json(out, payload)

        lote_updated = {**lote, "hook": elegido.get("texto") if isinstance(elegido, dict) else str(elegido)}
        save_json(ctx.paths["lote"], lote_updated)
        ctx.lote = lote_updated

        texto = lote_updated["hook"]
        return AgentResult(ok=True, artifacts=[str(out)], notes=f"Hook ({payload['modo']}): {texto[:55]}…")

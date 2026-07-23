"""HookAgent — ganchos de apertura (skill hooks-redes embebida en pipeline)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
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


class HookAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        tema = _base_tema(lote, context)
        promesa = _promesa(lote) or f"claridad práctica sobre {tema}"
        ideas = []
        guia = lote.get("guia") or {}
        if isinstance(guia, dict):
            ideas = list(guia.get("ideas") or guia.get("puntos") or [])[:3]

        hooks = [
            {
                "id": 1,
                "texto": f"Si {tema} te abruma, esto te ordena en minutos.",
                "angulo": "dolor",
            },
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

        elegido = hooks[0]
        if lote.get("hook"):
            elegido = {"id": 0, "texto": str(lote["hook"]), "angulo": "manual"}

        payload = {
            "skill": "hooks-redes",
            "tema": tema,
            "hooks": hooks,
            "elegido": elegido,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": "medium",
            "nota": "MVP heurístico; skill hooks-redes en chat puede refinar",
        }
        out = ctx.paths["hooks"]
        save_json(out, payload)

        # Persistir hook elegido en lote para guion
        lote_updated = {**lote, "hook": elegido["texto"]}
        save_json(ctx.paths["lote"], lote_updated)
        ctx.lote = lote_updated

        return AgentResult(
            ok=True,
            artifacts=[str(out)],
            notes=f"Hook: {elegido['texto'][:60]}…",
        )

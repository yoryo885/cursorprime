"""HookAgent — ganchos de apertura (promo o enseñanza)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.formato import formato_video
from src.fuente_guia import ideas_from_guia, load_fuente_texto
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


def _mock_hooks_promo(tema: str, promesa: str, ideas: list[str]) -> dict:
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


def _mock_hooks_ensenanza(tema: str, promesa: str, ideas: list[str]) -> dict:
    """Estilo canal educativo (curiosidad + insight), no venta."""
    idea0 = ideas[0] if ideas else promesa or tema
    corta = idea0 if len(idea0) < 90 else idea0[:87] + "…"
    hooks = [
        {
            "id": 1,
            "texto": f"Nadie te explica esto así: {corta}",
            "angulo": "insight",
        },
        {
            "id": 2,
            "texto": f"El 80% de tu cansancio no es lo que crees. Es un patrón.",
            "angulo": "revelacion",
        },
        {
            "id": 3,
            "texto": f"En 60 segundos entiendes por qué {tema} cambia cómo priorizas.",
            "angulo": "promesa_aprendizaje",
        },
    ]
    return {"hooks": hooks, "elegido": hooks[0], "confidence": "medium", "modo": "heuristica"}


class HookAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        formato = formato_video(lote, context)
        tema = _base_tema(lote, context)
        promesa = _promesa(lote) or f"claridad práctica sobre {tema}"
        guia = lote.get("guia") if isinstance(lote.get("guia"), dict) else {}
        fuente = lote.get("fuente_guia") or guia.get("fuente") or ""
        fuente_texto = load_fuente_texto(str(fuente)) if fuente else ""
        ideas = ideas_from_guia(guia, fuente_texto)[:3]

        mock = (
            _mock_hooks_ensenanza(tema, promesa, ideas)
            if formato == "ensenanza"
            else _mock_hooks_promo(tema, promesa, ideas)
        )
        data = mock
        if llm_activo() and not lote.get("hook"):
            if formato == "ensenanza":
                system = (
                    "Eres guionista de canal educativo faceless (estilo Psicología Invisible). "
                    "Hook de curiosidad/insight en 1 frase, sin vender, sin 'comenta X'. "
                    "JSON: hooks[{id,texto,angulo}], elegido."
                )
            else:
                system = (
                    "Eres copy de Reels/TikTok. Skill hooks-redes: máx 1 frase, sin saludo, "
                    "curiosidad o tensión en 3 segundos. JSON: hooks[{id,texto,angulo}], elegido."
                )
            user = f"Formato: {formato}\nTema: {tema}\nPromesa: {promesa}\nIdeas: {ideas}\nGenera 3 hooks."
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
            "formato": formato,
            "tema": tema,
            "hooks": hooks,
            "elegido": elegido,
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "confidence": data.get("confidence", "medium"),
            "modo": data.get("modo", "heuristica"),
            "nota": "ensenanza=insight; promo=venta. Ref: canales educativos faceless",
        }
        out = ctx.paths["hooks"]
        save_json(out, payload)

        lote_updated = {
            **lote,
            "hook": elegido.get("texto") if isinstance(elegido, dict) else str(elegido),
            "formato": formato,
        }
        save_json(ctx.paths["lote"], lote_updated)
        ctx.lote = lote_updated

        texto = lote_updated["hook"]
        return AgentResult(
            ok=True,
            artifacts=[str(out)],
            notes=f"Hook {formato} ({payload['modo']}): {texto[:50]}…",
        )

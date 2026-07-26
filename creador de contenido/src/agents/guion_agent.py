"""GuionAgent — promo (venta) o enseñanza (didáctico / Psicología Invisible)."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.formato import formato_video
from src.fuente_guia import ideas_from_guia, load_fuente_texto
from src.llm_client import get_llm, llm_activo
from src.types import AgentResult, PipelineContext


def _acortar_idea(texto: str, max_len: int = 110) -> str:
    """Acorta sin cortar a mitad de palabra ni dejar '…' a medias (promo)."""
    t = " ".join(str(texto).split())
    for pref in (
        "Verás que ",
        "Notarás que ",
        "Descubrirás que ",
        "Comprenderás que ",
        "Reconocerás que ",
        "Observarás que ",
        "Encontrarás que ",
    ):
        if t.startswith(pref):
            t = t[len(pref) :]
            t = t[0].upper() + t[1:] if t else t
            break
    if len(t) <= max_len:
        return t
    # preferir corte en frase
    cut = t[:max_len]
    for sep in (". ", "; ", ": ", ", "):
        idx = cut.rfind(sep)
        if idx >= max(40, max_len // 3):
            return cut[: idx + (1 if sep.startswith(".") else 0)].rstrip(" ,;:") + "."
    return cut.rsplit(" ", 1)[0].rstrip(" ,;:") + "."


def _frase_completa(texto: str) -> str:
    """Para enseñanza: nunca truncar con puntos suspensivos."""
    t = " ".join(str(texto).split()).strip()
    t = t.replace("…", "").replace("...", "").strip()
    return t


def build_guion_promo(titulo: str, hook: str, promesa: str, ideas: list[str], cta: str) -> str:
    bloques = [
        hook or f"Si quieres dominar {titulo}, quédate.",
        f"El problema: acumular PDFs sin un plan claro sobre {titulo}.",
        f"Esta guía te da {promesa or 'pasos accionables'} sin relleno.",
    ]
    for i, idea in enumerate(ideas[:3], start=1):
        bloques.append(f"{i}. {_acortar_idea(idea)}")
    bloques.append(cta or f"Descarga la guía «{titulo}» y aplícala hoy.")
    return "\n\n".join(bloques)


def build_guion_ensenanza(titulo: str, hook: str, promesa: str, ideas: list[str], cierre: str) -> str:
    """
    Estructura didáctica (ref. canales faceless educativos):
    hook → concepto → por qué importa → 2–3 enseñanzas → aplicación → cierre suave
    """
    i0 = _frase_completa(ideas[0]) if ideas else (promesa or titulo)
    i1 = _frase_completa(ideas[1]) if len(ideas) > 1 else "Separa lo vital de lo secundario."
    i2 = _frase_completa(ideas[2]) if len(ideas) > 2 else "Revisa tu prioridad cada semana."
    hook_limpio = _frase_completa(hook) if hook else f"Hay un patrón detrás de {titulo} que casi nadie nombra."
    # Evitar hook que ya viene truncado con resto de idea a medias
    if hook_limpio.endswith(" l") or hook_limpio.endswith(" tus") or len(hook_limpio) < 20:
        hook_limpio = f"Nadie te explica esto así: {i0}"
    bloques = [
        hook_limpio,
        f"La idea central: {i0}",
        f"Por qué importa: {promesa or 'dejas de dispersar energía en lo que no mueve resultados'}.",
        f"Primera enseñanza: {i1}",
        f"Segunda enseñanza: {i2}",
        "Cómo aplicarlo hoy: elige una lista de lo que haces, marca solo el 20% que más impacta, y protege tiempo para eso.",
        cierre
        or "Si esto te ordenó la cabeza, guarda el video. La próxima vez que te sientas abrumado, vuelve a esta regla.",
    ]
    return "\n\n".join(_frase_completa(b) for b in bloques)


class GuionAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})
        formato = formato_video(lote, context)
        modo = "heuristica"
        ideas: list[str] = []

        if lote.get("guion") and not lote.get("regenerar_guion"):
            guion = str(lote["guion"]).strip()
            origen = "guion_existente"
            titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
            modo = "guion_existente"
        else:
            guia = lote.get("guia") if isinstance(lote.get("guia"), dict) else {}
            fuente = lote.get("fuente_guia") or guia.get("fuente") or ""
            fuente_texto = load_fuente_texto(str(fuente)) if fuente else ""
            titulo = (
                guia.get("titulo")
                or context.get("titulo")
                or lote.get("titulo")
                or ctx.slug
            )
            promesa = guia.get("promesa") or guia.get("beneficio") or ""
            ideas = ideas_from_guia(guia, fuente_texto)
            if not ideas and context.get("temas"):
                ideas = [str(t) for t in context["temas"][:5]]
            if not ideas:
                ideas = ["idea clave 1", "idea clave 2", "cómo aplicarlo"]
            hook = lote.get("hook") or ""
            hooks_path = ctx.paths.get("hooks")
            hooks_data = load_json(hooks_path, {}) if hooks_path else {}
            if not hook and hooks_data:
                hook = (hooks_data.get("elegido") or {}).get("texto", "")
            cta = guia.get("cta") or lote.get("cta") or ""
            cierre = guia.get("cierre") or lote.get("cierre") or ""

            if formato == "ensenanza":
                guion = build_guion_ensenanza(str(titulo), hook, str(promesa), ideas, str(cierre))
            else:
                guion = build_guion_promo(str(titulo), hook, str(promesa), ideas, str(cta))
            origen = "guia" if guia or fuente_texto else "temas"

            if llm_activo():
                if formato == "ensenanza":
                    system = (
                        "Eres guionista de canal educativo faceless (estilo Psicología Invisible). "
                        "ENTREGA UNA ENSEÑANZA clara del concepto. No vendas. "
                        "Estructura: hook → concepto → por qué importa → 2 enseñanzas → aplicación hoy → cierre suave. "
                        "Escenas separadas por doble salto de línea. Español hablado, frases cortas. "
                        'JSON: {"guion":"...","mensaje_central":"..."}'
                    )
                else:
                    system = (
                        "Eres guionista de video corto promocional. Un mensaje central. "
                        "Escenas separadas por doble salto de línea. Español. "
                        'JSON: {"guion":"...","mensaje_central":"..."}'
                    )
                user = (
                    f"Formato: {formato}\nTítulo: {titulo}\nHook: {hook}\nPromesa: {promesa}\n"
                    f"Ideas del resumen (enseñar, no copiar PDF):\n- "
                    + "\n- ".join(ideas)
                    + "\nEscribe guion hablado."
                )
                try:
                    data = get_llm().complete_json(
                        system,
                        user,
                        mock_payload={"guion": guion, "mensaje_central": ideas[0] if ideas else titulo},
                    )
                    if data.get("guion"):
                        guion = str(data["guion"]).strip()
                        modo = "llm"
                        origen = f"{origen}+llm"
                except Exception:
                    modo = "heuristica_fallback"

        out_json = ctx.paths["guion"]
        out_md = ctx.paths["guion_md"]
        preview = [
            {"id": i + 1, "texto_guion": p.strip()}
            for i, p in enumerate(guion.split("\n\n"))
            if p.strip()
        ]
        payload = {
            "skill": "guion-a-video",
            "formato": formato,
            "titulo": titulo,
            "guion": guion,
            "escenas_preview": preview,
            "ideas": ideas,
            "generado_desde": origen,
            "modo": modo,
            "archivo_md": str(out_md),
            "generado_at": datetime.now(timezone.utc).isoformat(),
            "referencia_estilo": "ensenanza≈Psicología Invisible / faceless educativo"
            if formato == "ensenanza"
            else "promo",
        }
        save_json(out_json, payload)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(f"# Guion ({formato}) — {titulo}\n\n{guion}\n", encoding="utf-8")

        lote_updated = {**lote, "guion": guion, "titulo": titulo, "formato": formato}
        save_json(ctx.paths["lote"], lote_updated)
        ctx.lote = lote_updated
        context["guion"] = guion
        context["titulo"] = titulo
        context["formato"] = formato
        save_json(ctx.paths["context"], context)

        return AgentResult(
            ok=True,
            artifacts=[str(out_json), str(out_md)],
            notes=f"Guion {formato} ({origen}/{modo}) · {len(preview)} bloques",
        )

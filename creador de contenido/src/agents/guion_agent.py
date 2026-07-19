"""GuionAgent — arma guion promocional desde guía/PDF o temas."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT, load_json, save_json
from src.types import AgentResult, PipelineContext


def _load_fuente_texto(path_str: str) -> str:
    candidates = [
        Path(path_str),
        ROOT / path_str,
        ROOT.parent / path_str.lstrip("./"),
        ROOT.parent / path_str.replace("../", "", 1),
    ]
    path = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not path:
        return ""
    if path.suffix.lower() in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")[:4000]
    return ""


def _ideas_from_guia(guia: dict, fuente_texto: str) -> list[str]:
    ideas = list(guia.get("ideas") or guia.get("puntos") or [])
    if ideas:
        return [str(x) for x in ideas[:5]]
    if fuente_texto:
        lines = [ln.strip("-*# ").strip() for ln in fuente_texto.splitlines() if ln.strip()]
        bullets = [ln for ln in lines if 20 < len(ln) < 160][:5]
        if bullets:
            return bullets
    temas = guia.get("temas") or []
    return [str(t) for t in temas[:5]] or ["idea clave 1", "idea clave 2", "cómo aplicarlo"]


def build_guion_promo(titulo: str, hook: str, promesa: str, ideas: list[str], cta: str) -> str:
    bloques = [
        hook or f"Si quieres dominar {titulo}, quédate.",
        f"El problema: acumular PDFs sin un plan claro sobre {titulo}.",
        f"Esta guía te da {promesa or 'pasos accionables'} sin relleno.",
    ]
    for i, idea in enumerate(ideas[:3], start=1):
        bloques.append(f"{i}. {idea}")
    bloques.append(cta or f"Descarga la guía «{titulo}» y aplícala hoy.")
    return "\n\n".join(bloques)


class GuionAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        lote = load_json(ctx.paths["lote"], {}) or ctx.lote
        context = load_json(ctx.paths["context"], {})

        # Si ya hay guion explícito y no se fuerza regenerar, solo normaliza/exporta
        if lote.get("guion") and not lote.get("regenerar_guion"):
            guion = str(lote["guion"]).strip()
            origen = "guion_existente"
            ideas = []
            titulo = context.get("titulo") or lote.get("titulo") or ctx.slug
        else:
            guia = lote.get("guia") if isinstance(lote.get("guia"), dict) else {}
            fuente = lote.get("fuente_guia") or guia.get("fuente") or ""
            fuente_texto = _load_fuente_texto(str(fuente)) if fuente else ""
            titulo = (
                guia.get("titulo")
                or context.get("titulo")
                or lote.get("titulo")
                or ctx.slug
            )
            promesa = guia.get("promesa") or guia.get("beneficio") or ""
            ideas = _ideas_from_guia(guia, fuente_texto)
            if not ideas and context.get("temas"):
                ideas = [str(t) for t in context["temas"][:5]]
            hook = lote.get("hook") or ""
            hooks_path = ctx.paths.get("hooks")
            hooks_data = load_json(hooks_path, {}) if hooks_path else {}
            if not hook and hooks_data:
                hook = (hooks_data.get("elegido") or {}).get("texto", "")
            cta = guia.get("cta") or lote.get("cta") or ""
            guion = build_guion_promo(str(titulo), hook, str(promesa), ideas, str(cta))
            origen = "guia" if guia or fuente_texto else "temas"

        out_json = ctx.paths["guion"]
        out_md = ctx.paths["guion_md"]
        payload = {
            "skill": "guion-a-video",
            "titulo": titulo,
            "guion": guion,
            "escenas_preview": [
                {"id": i + 1, "texto_guion": p.strip()}
                for i, p in enumerate(guion.split("\n\n"))
                if p.strip()
            ],
            "ideas": ideas,
            "generado_desde": origen,
            "archivo_md": str(out_md),
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out_json, payload)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(f"# Guion — {titulo}\n\n{guion}\n", encoding="utf-8")

        lote_updated = {**lote, "guion": guion, "titulo": titulo}
        save_json(ctx.paths["lote"], lote_updated)
        ctx.lote = lote_updated

        context["guion"] = guion
        context["titulo"] = titulo
        save_json(ctx.paths["context"], context)

        return AgentResult(
            ok=True,
            artifacts=[str(out_json), str(out_md)],
            notes=f"Guion ({origen}) · {len(payload['escenas_preview'])} bloques",
        )

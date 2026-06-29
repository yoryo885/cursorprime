"""Empaqueta ideas y las copia a cola/pendientes."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import COLA_PENDIENTES, load_json, save_json
from src.types import AgentResult, PipelineContext


class PackagerLluviaAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        data = load_json(ctx.paths["ideas"], {})
        ideas = data.get("ideas") or []
        out = ctx.paths["output"]
        out.mkdir(parents=True, exist_ok=True)

        save_json(out / "ideas.json", data)

        lines = [
            f"# Lluvia de ideas — {data.get('tema', ctx.slug)}",
            "",
            "⚠️ **Ninguna idea se ejecuta sola.** Usa `cola aprobar` o `cola rechazar`.",
            "",
        ]
        by_cat: dict[str, list] = {}
        for idea in ideas:
            by_cat.setdefault(idea.get("categoria", "meta"), []).append(idea)

        for cat, items in sorted(by_cat.items()):
            lines.append(f"## {cat}")
            lines.append("")
            for idea in items:
                lines.append(f"### [{idea['id']}] {idea['titulo']}")
                lines.append(f"- **Proyecto:** {idea.get('proyecto_afectado')}")
                lines.append(f"- **Confianza:** {idea.get('confidence')}")
                lines.append(f"- **Problema:** {idea.get('problema')}")
                lines.append(f"- **Propuesta:** {idea.get('propuesta')}")
                lines.append("")

        md_path = out / "cola.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

        COLA_PENDIENTES.mkdir(parents=True, exist_ok=True)
        for idea in ideas:
            save_json(COLA_PENDIENTES / f"{idea['id']}.json", idea)

        manifest = {
            "slug": ctx.slug,
            "tipo": "lluvia",
            "ideas": len(ideas),
            "cola_pendientes": str(COLA_PENDIENTES),
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out / "manifest.json", manifest)
        return AgentResult(
            ok=True,
            artifacts=[str(out / "ideas.json"), str(md_path)],
            notes=f"{len(ideas)} ideas en cola/pendientes",
        )

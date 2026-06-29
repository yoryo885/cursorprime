"""Agente 4: viabilidad + DISEÑO.md legible."""

from __future__ import annotations

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class FeasibilityAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        brief = load_json(ctx.borrador_dir / "meta" / "brief.json", {})
        research = load_json(ctx.borrador_dir / "meta" / "research.json", {})
        plan = load_json(ctx.borrador_dir / "meta" / "plan.json", {})

        veredicto = "GO_CON_RESERVAS"
        if research.get("pendiente_manual"):
            veredicto = "GO_CON_RESERVAS"

        feasibility = {
            "slug": ctx.slug,
            "veredicto": veredicto,
            "mvp": [
                "Collector con mock o scrape limitado",
                "Calculadora margen ML Chile",
                "Reporte JSON + resumen TXT",
            ],
            "v1": [
                "Sync publicaciones ML",
                "Alertas de órdenes",
                "Stock guard",
            ],
            "futuro": ["Auto-compra solo si proveedor lo permite"],
            "bloqueadores": research.get("riesgos", []),
            "listo_para_construir": veredicto in ("GO", "GO_CON_RESERVAS"),
            "nota": "Revisar DISEÑO.md antes de decir construye",
        }

        meta = ctx.borrador_dir / "meta"
        feas_path = meta / "feasibility.json"
        save_json(feas_path, feasibility)

        pasos = plan.get("pipeline") or []
        diseno_md = self._render_diseno(brief, feasibility, pasos)
        diseno_path = ctx.borrador_dir / "DISEÑO.md"
        diseno_path.write_text(diseno_md, encoding="utf-8")

        return AgentResult(
            ok=True,
            artifacts=[str(feas_path), str(diseno_path)],
            notes=f"Veredicto: {veredicto}",
        )

    def _render_diseno(self, brief: dict, feasibility: dict, pasos: list) -> str:
        lines = [
            f"# Diseño — {brief.get('nombre', 'Proyecto')}",
            "",
            "## Problema",
            brief.get("problema", ""),
            "",
            "## Modelo",
            brief.get("modelo_negocio", ""),
            "",
            f"## Veredicto: **{feasibility.get('veredicto')}**",
            "",
            "### MVP",
        ]
        lines.extend(f"- {x}" for x in feasibility.get("mvp", []))
        lines.extend(["", "### Pipeline destino", ""])
        for p in pasos:
            lines.append(f"{p.get('id')}. **{p.get('nombre')}** (`{p.get('slug')}`) → `{p.get('agente')}`")
        lines.extend(
            [
                "",
                "## Siguiente paso",
                "",
                "Cuando estés conforme con este diseño, di en New Agent:",
                "",
                f"> **Construye el proyecto {brief.get('slug', 'slug')} — está listo**",
                "",
                "Hasta entonces **no** se creará nada en `proyectos/`.",
            ]
        )
        return "\n".join(lines)

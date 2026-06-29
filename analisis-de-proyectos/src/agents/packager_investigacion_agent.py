"""Empaqueta análisis de investigación."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PackagerInvestigacionAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        analisis = load_json(ctx.paths["analisis"], {})
        fetch = load_json(ctx.paths["fetch"], {})
        out = ctx.paths["output"]
        out.mkdir(parents=True, exist_ok=True)

        json_path = out / "analisis.json"
        save_json(json_path, analisis)

        lines = [
            f"# Análisis — {analisis.get('tema', ctx.slug)}",
            "",
            f"*Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
            "",
            "## Resumen",
            "",
            analisis.get("resumen_ejecutivo", ""),
            "",
            "## Productos que funcionan hoy",
            "",
        ]
        for p in analisis.get("productos_que_funcionan") or []:
            lines.append(f"- {p}")
        lines.extend(["", "## Patrones", ""])
        for p in analisis.get("patrones") or []:
            lines.append(f"- {p}")
        lines.extend(["", "## Oportunidades pipeline", ""])
        for op in analisis.get("oportunidades_pipeline") or []:
            lines.append(f"- **{op.get('titulo')}** (conf. {op.get('confidence')}) — {op.get('razon')}")
        lines.extend(["", "## Fuentes", ""])
        for f in analisis.get("fuentes") or []:
            lines.append(f"- [{f.get('titulo')}]({f.get('url')}) ({f.get('tipo')})")
        lines.extend(["", f"---", f"Resultados crudos: {fetch.get('total', 0)} ({'mock' if fetch.get('mock') else 'live'})"])

        md_path = out / "analisis.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

        manifest = {
            "slug": ctx.slug,
            "tipo": "investigacion",
            "tema": analisis.get("tema"),
            "output": {"analisis_json": str(json_path), "analisis_md": str(md_path)},
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out / "manifest.json", manifest)
        return AgentResult(ok=True, artifacts=[str(json_path), str(md_path)])

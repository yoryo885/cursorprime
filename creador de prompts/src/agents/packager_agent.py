"""Empaqueta prompts en JSON + Markdown."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        qc = load_json(ctx.paths["qc"], {})
        data = load_json(ctx.paths["prompts"], {})

        out_dir = ctx.paths["output"]
        out_dir.mkdir(parents=True, exist_ok=True)

        json_path = out_dir / "prompts.json"
        save_json(json_path, data)

        md_lines = [
            f"# Prompts — {context.get('titulo')}",
            "",
            f"- **Tipo:** {context.get('tipo')}",
            f"- **Proyecto:** {context.get('proyecto_destino')}",
            f"- **Generado:** {datetime.now(timezone.utc).isoformat()}",
            "",
        ]

        for item in data.get("prompts", []):
            md_lines.extend(
                [
                    f"## {item.get('tema')} (v{item.get('variante')})",
                    "",
                    "```",
                    item.get("prompt", ""),
                    "```",
                    "",
                ]
            )
            if item.get("negative"):
                md_lines.extend(["**Negative:**", "", item["negative"], ""])

        md_path = out_dir / "prompts.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        manifest = {
            "slug": ctx.slug,
            "tipo": context.get("tipo"),
            "proyecto_destino": context.get("proyecto_destino"),
            "count": data.get("count", 0),
            "qc_ok": qc.get("ok", False),
            "archivos": [json_path.name, md_path.name],
        }
        save_json(out_dir / "manifest.json", manifest)

        return AgentResult(ok=True, artifacts=[str(md_path), str(json_path)], notes=md_path.name)

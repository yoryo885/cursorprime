"""Genera PDF vía script vendor (opcional)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

from src.config import VENDOR_ROOT, load_json, save_json
from src.types import AgentResult, PipelineContext


class PdfAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        if not ctx.flags.get("pdf"):
            return AgentResult(ok=True, notes="PDF omitido (usa --pdf)")

        syn = load_json(ctx.paths["synthesis"], {})
        out = ctx.paths["output"]
        pdf_path = out / "MARKETING-REPORT.pdf"
        json_path = out / "pdf_input.json"

        categories = {}
        for name, data in (syn.get("categories") or {}).items():
            categories[name] = {"score": data.get("score"), "weight": data.get("weight")}

        pdf_data = {
            "url": syn.get("url"),
            "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "brand_name": syn.get("brand_name"),
            "overall_score": syn.get("overall_score"),
            "executive_summary": (
                f"Marketing score {syn.get('overall_score')}/100 ({syn.get('grade')}). "
                f"Ver MARKETING-AUDIT.md para detalle completo."
            ),
            "categories": categories,
            "findings": [
                {
                    "severity": f.get("severity"),
                    "title": f.get("title"),
                    "description": f.get("detail"),
                }
                for f in (syn.get("findings") or [])[:10]
            ],
            "action_plan": {
                "quick_wins": syn.get("quick_wins") or [],
            },
        }
        save_json(json_path, pdf_data)

        script = VENDOR_ROOT / "scripts" / "generate_pdf_report.py"
        if not script.exists():
            return AgentResult(
                ok=False,
                notes="Script PDF no encontrado en vendor/ai-marketing-claude",
            )

        try:
            subprocess.run(
                [sys.executable, str(script), str(json_path), str(pdf_path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as exc:
            return AgentResult(
                ok=False,
                notes=f"PDF falló: {exc.stderr or exc}",
                warnings=["Entregar MARKETING-AUDIT.md como fallback"],
            )
        except FileNotFoundError:
            return AgentResult(ok=False, notes="Python subprocess error")

        if not pdf_path.exists():
            return AgentResult(ok=False, notes="PDF no generado")

        return AgentResult(ok=True, artifacts=[str(pdf_path)], notes="PDF generado")

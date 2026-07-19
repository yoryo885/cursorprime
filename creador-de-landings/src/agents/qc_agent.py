"""QC mínimo de la landing."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        preview = ctx.paths["preview"]
        brief = load_json(ctx.paths["brief"], {}) or {}
        checks = {
            "archivo_html": preview.exists() and preview.stat().st_size > 200,
            "tiene_marca": bool(brief.get("marca")),
            "tiene_headline": bool(brief.get("promesa") or brief.get("producto")),
            "tiene_cta": bool(brief.get("cta")),
            "tiene_estilo": brief.get("estilo") in ("editorial", "mockup", "oferta"),
        }
        if preview.exists():
            html = preview.read_text(encoding="utf-8")
            checks["html_tiene_cta"] = 'class="btn"' in html or "btn " in html
            checks["html_tiene_marca"] = bool(brief.get("marca")) and brief["marca"] in html

        ok = all(checks.values())
        report = {"ok": ok, "checks": checks}
        save_json(ctx.paths["qc"], report)
        if not ok:
            failed = [k for k, v in checks.items() if not v]
            return AgentResult(ok=False, notes=f"QC falló: {', '.join(failed)}")
        return AgentResult(ok=True, artifacts=[str(ctx.paths["qc"])], notes="QC ok")

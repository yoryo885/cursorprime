"""Agente 7: QC del proyecto construido."""

from __future__ import annotations

from src.config import load_json, save_json
from src.models import AgentResult, PipelineContext


class ProjectQCAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        if not ctx.autorizado_construir:
            raise PermissionError("Construcción bloqueada.")

        slug = ctx.slug
        root = ctx.proyecto_dir
        checks = []

        main_candidates = list(root.glob(f"{slug}_main.py"))
        checks.append(
            {
                "nombre": "cli_main",
                "ok": bool(main_candidates),
                "detalle": str(main_candidates[0]) if main_candidates else "falta {slug}_main.py",
            }
        )

        plan_path = root / "meta" / "plan.json"
        plan = load_json(plan_path, {})
        checks.append(
            {
                "nombre": "plan_json",
                "ok": bool(plan.get("pipeline")),
                "detalle": f"{len(plan.get('pipeline') or [])} pasos",
            }
        )

        entrega_ok = (root / "ENTREGA.txt").exists()
        checks.append({"nombre": "entrega_txt", "ok": entrega_ok, "detalle": "ENTREGA.txt"})

        all_ok = all(c["ok"] for c in checks)
        report = {
            "slug": slug,
            "ok": all_ok,
            "checks": checks,
        }
        out = root / "meta" / "qc_report.json"
        save_json(out, report)

        return AgentResult(
            ok=all_ok,
            artifacts=[str(out)],
            notes="QC OK" if all_ok else "QC con fallos",
        )

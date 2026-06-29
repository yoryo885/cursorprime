"""Agente 12 — Report."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class ReportAgent:
    key = "report"

    def run(self, ctx: PipelineContext) -> AgentResult:
        idea = ctx.idea
        verdict = load_json(ctx.paths["synthesis"], {})
        plan = load_json(ctx.paths.get("planner"), {})
        qc = load_json(ctx.paths.get("qc"), {})
        out = ctx.paths["output"]
        out.mkdir(parents=True, exist_ok=True)

        report = {
            "slug": ctx.slug,
            "titulo": idea.get("titulo", ctx.slug),
            "veredicto": verdict,
            "plan_accion": plan,
            "qc_ok": qc.get("ok"),
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out / "report.json", report)

        sg = verdict.get("score_global", {})
        md = [
            f"# Project Lens — {idea.get('titulo', ctx.slug)}",
            "",
            f"**Veredicto:** {verdict.get('veredicto', '?').upper()}",
            f"**Score:** {sg.get('point', '?')} ({sg.get('min')}-{sg.get('max')})",
            f"**Confianza global:** {int(verdict.get('confidence_global', 0) * 100)}%",
            "",
            "## Recomendación",
            verdict.get("recomendacion", ""),
            "",
            "## Siguiente paso",
            verdict.get("siguiente_paso", ""),
            "",
            "## QC",
            f"{'OK' if qc.get('ok') else 'REVISAR'}",
        ]
        (out / "resumen.md").write_text("\n".join(md), encoding="utf-8")

        plan_lines = ["# Plan de acción", ""]
        for f in plan.get("fases", []):
            plan_lines.append(f"## Fase {f.get('id')}: {f.get('nombre')}")
            plan_lines.append(f"*{f.get('objetivo')}*")
            for t in f.get("tareas", []):
                plan_lines.append(f"- [{t.get('prioridad')}] {t.get('tarea')}")
            plan_lines.append("")
        (out / "plan.md").write_text("\n".join(plan_lines), encoding="utf-8")

        canvas = self._canvas_tsx(ctx.slug, verdict, plan)
        (out / "dashboard.canvas.tsx").write_text(canvas, encoding="utf-8")

        return AgentResult(
            ok=True,
            artifacts=[str(out / "report.json"), str(out / "resumen.md"), str(out / "dashboard.canvas.tsx")],
            notes="report.json + resumen.md + plan.md + canvas",
        )

    def _canvas_tsx(self, slug: str, verdict: dict, plan: dict) -> str:
        sg = verdict.get("score_global", {})
        areas = verdict.get("por_area", {})
        rows = "".join(
            f'    {{ label: "{k}", score: {v.get("score", 0)} }},\n' for k, v in areas.items()
        )
        accion = plan.get("siguiente_accion_inmediata", "")
        return f'''/** Project Lens dashboard — {slug} */
export default function Dashboard() {{
  const veredicto = "{verdict.get("veredicto", "?")}";
  const score = {sg.get("point", 0)};
  const areas = [
{rows}  ];
  const siguiente = "{accion}";
  return (
    <div style={{ fontFamily: "system-ui", padding: 24, maxWidth: 720 }}>
      <h1>Project Lens — {slug}</h1>
      <p>Veredicto: <strong>{{veredicto}}</strong> · Score {{score}}</p>
      <ul>
        {{areas.map((a) => (
          <li key={{a.label}}>{{a.label}}: {{a.score}}</li>
        ))}}
      </ul>
      <p>Siguiente: {{siguiente}}</p>
    </div>
  );
}}
'''

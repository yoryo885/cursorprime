"""Empaqueta informe en español — MD + HTML vendible."""

from __future__ import annotations

from datetime import datetime, timezone

from src.client_language import PRIORIDAD_PESO, SEVERIDAD_CLIENTE, TIPO_NEGOCIO_ES, resumen_ejecutivo
from src.config import load_json, save_json, ROOT, ASSETS_DIR
from src.html_report import CATEGORIAS_ES, generar_html
from src.types import AgentResult, PipelineContext


class PackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        syn = load_json(ctx.paths["synthesis"], {})
        out = ctx.paths["output"]
        out.mkdir(parents=True, exist_ok=True)

        fecha = datetime.now(timezone.utc).strftime("%d/%m/%Y")
        score = syn.get("overall_score")
        grade = syn.get("grade")

        brand = syn.get("brand_name", ctx.slug)
        tipo = TIPO_NEGOCIO_ES.get(syn.get("business_type", "general"), "Negocio")

        lines = [
            f"# Informe de marketing digital — {brand}",
            "",
            f"**Sitio web:** {syn.get('url')}",
            f"**Fecha:** {fecha}",
            f"**Tipo de negocio:** {tipo}",
            f"**Puntuación general: {score}/100**",
            "",
            "---",
            "",
            "## En pocas palabras",
            "",
            resumen_ejecutivo(score or 0, grade or "C", brand),
            "",
            "## Cómo va cada área",
            "",
            "| Área | Nota | Prioridad |",
            "|------|------|-----------|",
        ]
        for cat, data in (syn.get("categories") or {}).items():
            nombre = CATEGORIAS_ES.get(cat, cat)
            prio = PRIORIDAD_PESO.get(str(data.get("weight")), data.get("weight"))
            lines.append(f"| {nombre} | {data.get('score')}/100 | {prio} |")

        lines.extend(["", "## Qué encontramos (en lenguaje claro)", ""])
        for f in syn.get("findings") or []:
            sev = SEVERIDAD_CLIENTE.get(f.get("severity", "medium"), "A mejorar")
            lines.append(f"- **[{sev}]** {f.get('client_title', f.get('title'))}")
            lines.append(f"  - {f.get('client_detail', f.get('detail'))}")
            lines.append(f"  - *Qué hacer:* {f.get('client_action', '')}")

        lines.extend(["", "## Mejoras rápidas (esta semana)", ""])
        for i, w in enumerate(syn.get("quick_wins") or [], 1):
            lines.append(f"{i}. {w}")

        if syn.get("competitors"):
            lines.extend(["", "## Otros negocios similares en tu zona", ""])
            for c in syn["competitors"][:5]:
                tier = {"direct": "competidor directo", "aspirational": "referente del rubro"}.get(
                    c.get("tier", ""), ""
                )
                extra = f" ({tier})" if tier else ""
                lines.append(f"- **{c.get('name')}**{extra}")

        lines.extend(["", "## Próximo paso", "", "Agendar una llamada para revisar el plan de mejora — sin compromiso.", ""])

        md_path = out / "MARKETING-AUDIT.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

        context = load_json(ctx.paths["context"], {})
        branding = context.get("branding") or {}
        logo_src = ROOT / branding.get("logo", "assets/logo.svg")
        if not logo_src.is_absolute():
            logo_src = ROOT / logo_src
        if logo_src.exists():
            import shutil
            shutil.copy2(logo_src, out / logo_src.name)

        html_path = generar_html(syn, out / "MARKETING-AUDIT.html", branding)
        save_json(out / "audit.json", syn)

        manifest = {
            "slug": ctx.slug,
            "output": {
                "markdown": str(md_path),
                "html": str(html_path),
                "json": str(out / "audit.json"),
            },
            "score": score,
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out / "manifest.json", manifest)
        return AgentResult(ok=True, artifacts=[str(md_path), str(html_path), str(out / "audit.json")])

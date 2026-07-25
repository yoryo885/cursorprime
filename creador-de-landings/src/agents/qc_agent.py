"""QC de la landing (constitution + checks HTML)."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        preview = ctx.paths["preview"]
        brief = load_json(ctx.paths["brief"], {}) or {}
        qc_min = (ctx.constitution or {}).get("qc_minimo") or {}

        productos = brief.get("productos") or []
        checks: dict[str, bool] = {
            "archivo_html": preview.exists() and preview.stat().st_size > 200,
            "tiene_marca": bool(brief.get("marca")),
            "tiene_headline": bool(brief.get("promesa") or brief.get("producto")),
            "tiene_cta": bool(brief.get("cta")),
            "tiene_estilo": brief.get("estilo") in ("editorial", "mockup", "oferta", "tienda"),
            # 1 producto alcanza (antes exigía ≥2 y bloqueaba landings simples)
            "tiene_catalogo": len(productos) >= 1 if brief.get("mostrar_catalogo") else True,
        }

        # constitution.json → flags que deben ser true
        for key, required in qc_min.items():
            if required is True and key not in checks:
                checks[key] = False  # se completa abajo si aplica

        if preview.exists():
            html = preview.read_text(encoding="utf-8")
            marca = str(brief.get("marca") or "")
            checks["html_tiene_cta"] = 'class="btn"' in html or "btn " in html
            checks["html_tiene_marca"] = bool(marca) and marca in html
            checks["html_tiene_grid"] = (
                'id="guias"' in html or "data-rol-card" in html or "guia-card" in html
            )
            # Hero visual: sección hero o marca hero-level (no solo nav)
            checks["tiene_hero_visual"] = (
                'class="hero' in html
                or 'class="hero-nuevo"' in html
                or "brand-hero" in html
                or 'class="hero"' in html
            )
            # No inventar reseñas: si hay testimonio sin [PENDIENTE] y no es nota honesta, ok;
            # fallar solo si aparecen estrellas inventadas típicas
            fake_stars = ("★★★★★" in html) or ("5/5" in html and "inventad" not in html.lower())
            checks["sin_estrellas_inventadas"] = not fake_stars
        else:
            checks["html_tiene_cta"] = False
            checks["html_tiene_marca"] = False
            checks["tiene_hero_visual"] = False
            checks["sin_estrellas_inventadas"] = False

        # Alinear keys de constitution
        if "tiene_hero_visual" in qc_min:
            checks["tiene_hero_visual"] = bool(checks.get("tiene_hero_visual"))
        if "archivo_html" in qc_min:
            checks["archivo_html"] = bool(checks.get("archivo_html"))

        score = int(100 * sum(1 for v in checks.values() if v) / max(len(checks), 1))
        ok = all(checks.values())
        report = {
            "ok": ok,
            "score": score,
            "checks": checks,
            "constitution_aplicada": bool(qc_min),
            "n_productos": len(productos),
        }
        save_json(ctx.paths["qc"], report)
        if not ok:
            failed = [k for k, v in checks.items() if not v]
            return AgentResult(ok=False, notes=f"QC falló ({score}): {', '.join(failed)}")
        return AgentResult(
            ok=True,
            artifacts=[str(ctx.paths["qc"])],
            notes=f"QC ok score={score}",
        )

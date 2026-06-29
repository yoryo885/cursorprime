"""Agente 5: empaqueta listing en JSON y TXT listos para KDP."""
from __future__ import annotations

import json
from pathlib import Path

from src.marketing.constitution import assert_output_path_allowed
from src.marketing.context_loader import MarketingContext
from src.marketing.models import KDPListing
from src.marketing.seed_diff import compute_diff_vs_seed
from src.marketing.utils import kdp_output_dir
from src.serie import load_serie_config


class PackagerAgent:
    JSON_NAME = "amazon_listing.json"
    TXT_NAME = "amazon_listing.txt"

    def run(
        self,
        listing: KDPListing,
        marketing_ctx: MarketingContext | None = None,
    ) -> tuple[Path, Path]:
        seed = marketing_ctx.kdp_seed if marketing_ctx else {}
        listing.diff_vs_seed = compute_diff_vs_seed(
            titulo=listing.titulo,
            subtitulo=listing.subtitulo,
            keywords=listing.keywords,
            seed=seed,
        )

        out_dir = assert_output_path_allowed(kdp_output_dir(Path(listing.pdf_origen)))
        out_dir.mkdir(parents=True, exist_ok=True)

        json_path = out_dir / self.JSON_NAME
        txt_path = out_dir / self.TXT_NAME

        json_path.write_text(
            json.dumps(listing.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        txt_path.write_text(self._format_txt(listing), encoding="utf-8")
        return json_path, txt_path

    def _format_txt(self, listing: KDPListing) -> str:
        cfg = load_serie_config()
        sep = "=" * 60
        lines = [
            sep,
            "LISTING AMAZON KDP — LISTO PARA COPIAR",
            sep,
            "",
            f"Serie: {listing.serie or cfg.get('nombre_serie', '')}",
            f"PDF origen: {listing.pdf_origen}",
            f"Generado: {listing.generado_en}",
            "",
        ]
        if listing.titulo_pdf:
            lines.extend([
                f"Título portada PDF (referencia): {listing.titulo_pdf}",
                "",
            ])

        lines.extend([
            "— TÍTULO (máx. 200 caracteres) —",
            listing.titulo,
            f"({len(listing.titulo)} caracteres)",
            "",
        ])
        if listing.subtitulo:
            lines.extend([
                "— SUBTÍTULO (opcional, máx. 200) —",
                listing.subtitulo,
                f"({len(listing.subtitulo)} caracteres)",
                "",
            ])
        if listing.titulo_alternativas:
            lines.append("— TÍTULOS ALTERNATIVOS (A/B) —")
            for i, alt in enumerate(listing.titulo_alternativas, 1):
                lines.append(f"{i}. {alt}")
            lines.append("")

        lines.extend([
            "— DESCRIPCIÓN (HTML para KDP) —",
            listing.descripcion_html,
            "",
            "— 7 KEYWORDS —",
        ])
        for i, kw in enumerate(listing.keywords, 1):
            lines.append(f"{i}. {kw}")

        lines.extend(["", "— 5 BENEFICIOS DEL PRODUCTO —"])
        for i, b in enumerate(listing.beneficios, 1):
            if b:
                lines.append(f"{i}. {b}")

        if listing.categorias_bisac:
            lines.extend(["", "— CATEGORÍAS BISAC (sugeridas) —"])
            for cat in listing.categorias_bisac:
                lines.append(f"· {cat}")

        if listing.mercados:
            lines.extend(["", "— MERCADOS —", ", ".join(listing.mercados)])
        if listing.precio_usd:
            lines.extend(["", f"— PRECIO SUGERIDO — ${listing.precio_usd:.2f} USD"])

        if listing.disclaimer:
            lines.extend(["", "— DISCLAIMER —", listing.disclaimer])

        lines.extend([
            "",
            f"— CALIDAD (QC) — Score: {listing.qc_score}/10",
        ])
        if listing.qc_issues:
            lines.append("Issues: " + ", ".join(listing.qc_issues))
        if listing.qc_warnings:
            for w in listing.qc_warnings[:8]:
                lines.append(f"  ⚠ {w}")

        if listing.alignment_fixes:
            lines.extend(["", "— CORRECCIONES DE ALINEACIÓN —"])
            for fix in listing.alignment_fixes:
                lines.append(f"  · {fix}")

        if listing.diff_vs_seed:
            lines.extend(["", "— CAMBIOS VS BORRADOR (meta/kdp_listing.json) —"])
            for campo, detalle in listing.diff_vs_seed.items():
                lines.append(f"  {campo}: {detalle}")
        elif listing.seed_titulo_kdp:
            lines.extend([
                "",
                "— BORRADOR — Sin cambios relevantes vs meta/kdp_listing.json",
            ])

        a = listing.analisis
        lines.extend(
            [
                "",
                sep,
                "ANÁLISIS INTERNO (referencia)",
                sep,
                f"Tema principal: {a.tema_principal}",
                f"Libro fuente: {a.libro_fuente}",
                f"Audiencia: {a.audiencia}",
                f"Propuesta de valor: {a.propuesta_valor}",
            ]
        )
        return "\n".join(lines) + "\n"

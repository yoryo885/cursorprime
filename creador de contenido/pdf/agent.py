"""Módulo PDF — maqueta PNG en documento."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PdfModule:
    slug_modulo = "pdf"

    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        imgs = load_json(ctx.paths["generated_imagenes"], {}).get("imagenes", [])
        pdf_dir = ctx.paths["pdf_out"]
        pdf_dir.mkdir(parents=True, exist_ok=True)

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfgen import canvas
        except ImportError:
            return AgentResult(ok=False, notes="Instala reportlab: pip install reportlab")

        pdf_path = pdf_dir / f"{ctx.slug}.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, h - 50, context.get("titulo", ctx.slug)[:60])
        c.setFont("Helvetica", 11)
        c.drawString(50, h - 75, "Creador de Contenido — mock MVP")

        y = h - 120
        for img in imgs:
            p = Path(img["path"])
            if not p.exists():
                continue
            if y < 200:
                c.showPage()
                y = h - 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, img["tema"][:40])
            y -= 20
            reader = ImageReader(str(p))
            iw, ih = reader.getSize()
            scale = min((w - 100) / iw, 300 / ih)
            c.drawImage(reader, 50, y - ih * scale, iw * scale, ih * scale)
            y -= ih * scale + 30

        c.save()
        item = {
            "archivo": pdf_path.name,
            "path": str(pdf_path),
            "modulo": "pdf",
            "paginas": len(imgs) + 1,
            "generado_at": datetime.now(timezone.utc).isoformat(),
        }
        out = ctx.paths["generated_pdf"]
        save_json(out, {"pdf": [item], "count": 1})
        return AgentResult(ok=True, artifacts=[str(pdf_path)], notes=f"PDF: {pdf_path.name}")

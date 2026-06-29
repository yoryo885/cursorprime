"""Empaqueta todos los módulos generados."""

from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


class PackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        qc = load_json(ctx.paths["qc"], {})

        manifest = {
            "proyecto": "creador-de-contenido",
            "slug": ctx.slug,
            "titulo": context.get("titulo"),
            "salidas_pedidas": context.get("salidas_pedidas"),
            "salidas_generadas": context.get("salidas_efectivas"),
            "integracion_externa": False,
            "modulos": {},
            "qc_ok": qc.get("ok", False),
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest["video_modo"] = (context.get("video") or {}).get("modo", "slideshow")
        if ctx.paths.get("escenas") and Path(ctx.paths["escenas"]).exists():
            manifest["escenas"] = load_json(ctx.paths["escenas"], {})

        for key in ("generated_imagenes", "generated_gifs", "generated_videos", "generated_pdf"):
            if ctx.paths.get(key) and Path(ctx.paths[key]).exists():
                manifest["modulos"][key] = load_json(ctx.paths[key], {})

        out_dir = ctx.paths["output"]
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = out_dir / "manifest.json"
        save_json(manifest_path, manifest)

        zip_path = out_dir / f"{ctx.slug}_contenido.zip"
        carpetas = [
            ("imagenes", ctx.paths["imagenes_out"]),
            ("gifs", ctx.paths["gifs_out"]),
            ("videos", ctx.paths["videos_out"]),
            ("pdf", ctx.paths["pdf_out"]),
        ]
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(manifest_path, "manifest.json")
            for nombre, carpeta in carpetas:
                if not carpeta.exists():
                    continue
                for f in carpeta.rglob("*"):
                    if f.is_file() and not f.name.startswith("_"):
                        rel = f.relative_to(carpeta)
                        zf.write(f, f"{nombre}/{rel.as_posix()}")

        resumen = out_dir / "resumen.txt"
        resumen.write_text(
            f"Creador de Contenido — {context.get('titulo')}\n"
            f"Salidas: {', '.join(context.get('salidas_pedidas', []))}\n"
            f"QC: {'OK' if qc.get('ok') else 'FAIL'}\n"
            f"Pack: {zip_path.name}\n",
            encoding="utf-8",
        )
        return AgentResult(ok=True, artifacts=[str(zip_path)], notes=zip_path.name)

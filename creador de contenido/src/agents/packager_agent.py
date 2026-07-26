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
        plan = load_json(ctx.paths.get("plan_runtime"), {}) if ctx.paths.get("plan_runtime") else {}

        manifest = {
            "proyecto": "creador-de-contenido",
            "slug": ctx.slug,
            "titulo": context.get("titulo"),
            "receta": context.get("receta") or plan.get("receta"),
            "skills_activadas": context.get("skills_activadas") or plan.get("skills") or [],
            "agentes": plan.get("agentes") or context.get("agentes_plan") or [],
            "salidas_pedidas": context.get("salidas_pedidas"),
            "salidas_generadas": context.get("salidas_efectivas"),
            "integracion_externa": False,
            "modulos": {},
            "copy": {},
            "qc_ok": qc.get("ok", False),
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest["video_modo"] = (context.get("video") or {}).get("modo", "slideshow")
        if ctx.paths.get("escenas") and Path(ctx.paths["escenas"]).exists():
            manifest["escenas"] = load_json(ctx.paths["escenas"], {})

        for key in ("generated_imagenes", "generated_gifs", "generated_videos", "generated_pdf"):
            if ctx.paths.get(key) and Path(ctx.paths[key]).exists():
                manifest["modulos"][key] = load_json(ctx.paths[key], {})

        for key in ("hooks", "guion", "captions", "thumbnail", "audio"):
            if ctx.paths.get(key) and Path(ctx.paths[key]).exists():
                manifest["copy"][key] = load_json(ctx.paths[key], {})

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
            ("copy", ctx.paths["copy_dir"]),
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
        skills = ", ".join(manifest["skills_activadas"]) or "—"
        # Ruta clara del video final para el operador
        videos_dir = Path(ctx.paths["videos_out"])
        final_candidates = [
            videos_dir / f"{ctx.slug}.mp4",
            videos_dir / f"{ctx.slug}_subtitulado.mp4",
            videos_dir / f"{ctx.slug}_audio.mp4",
            out_dir / f"{ctx.slug}.mp4",
        ]
        final_video = next((p for p in final_candidates if p.exists() and p.stat().st_size > 50_000), None)
        if final_video and final_video.parent != out_dir:
            try:
                (out_dir / final_video.name).write_bytes(final_video.read_bytes())
            except Exception:
                pass
        video_line = f"Video final: {final_video}" if final_video else "Video final: (pendiente)"
        resumen.write_text(
            f"Creador de Contenido — {context.get('titulo')}\n"
            f"Receta: {manifest.get('receta')}\n"
            f"Skills: {skills}\n"
            f"Salidas: {', '.join(context.get('salidas_pedidas', []))}\n"
            f"QC: {'OK' if qc.get('ok') else 'FAIL'}\n"
            f"Pack: {zip_path.name}\n"
            f"{video_line}\n"
            f"Carpeta videos: {videos_dir}\n",
            encoding="utf-8",
        )
        artifacts = [str(zip_path), str(resumen)]
        if final_video:
            artifacts.append(str(final_video))
        return AgentResult(ok=True, artifacts=artifacts, notes=zip_path.name)

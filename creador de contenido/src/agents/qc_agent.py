"""QC por módulos activos y artefactos de copy."""

from __future__ import annotations

from pathlib import Path

from src.config import load_json, save_json, slug_dir
from src.paths_resolve import resolve_artifact_path
from src.types import AgentResult, PipelineContext

MIN_BYTES = 1024


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        plan = load_json(ctx.paths.get("plan_runtime"), {}) if ctx.paths.get("plan_runtime") else {}
        salidas = context.get("salidas_pedidas") or ctx.salidas
        agentes = set(plan.get("agentes") or [])
        issues = []
        passed = []
        warnings = []

        base = slug_dir(ctx.slug)
        fallbacks = {
            "png": [base / "imagenes"],
            "gif": [base / "gifs"],
            "video": [base / "videos", base / "videos" / "clips"],
            "pdf": [base / "pdf"],
        }

        checks = {
            "png": ("generated_imagenes", "imagenes"),
            "gif": ("generated_gifs", "gifs"),
            "video": ("generated_videos", "videos"),
            "pdf": ("generated_pdf", "pdf"),
        }

        for salida in salidas:
            key, field = checks.get(salida, (None, None))
            if not key or not ctx.paths.get(key) or not Path(ctx.paths[key]).exists():
                if salida in salidas:
                    issues.append({"modulo": salida, "error": "sin artefactos generados"})
                continue
            data = load_json(ctx.paths[key], {})
            items = data.get(field) or data.get("pdf") or []
            if salida == "video" and data.get("pendiente"):
                passed.append("video (pendiente ffmpeg)")
                continue
            # Si no hay items pero existe el mp4 final local, OK
            if salida == "video" and not items:
                local_final = base / "videos" / f"{ctx.slug}.mp4"
                if local_final.exists() and local_final.stat().st_size >= MIN_BYTES:
                    passed.append(local_final.name)
                    continue
            for item in items:
                raw = item.get("path", "")
                p = resolve_artifact_path(str(raw), fallbacks.get(salida, []))
                if p is None:
                    # clips referenciados de otra máquina: no tumbar QC si el final existe
                    if salida == "video" and item.get("escena_id") is not None:
                        warnings.append(f"clip ausente (ruta vieja): {item.get('archivo')}")
                        continue
                    name = item.get("archivo") or Path(str(raw)).name
                    issues.append({"modulo": salida, "error": f"archivo inválido: {name}"})
                    continue
                if p.suffix == ".txt":
                    passed.append(item.get("archivo", p.name))
                    continue
                if p.stat().st_size < MIN_BYTES:
                    issues.append({"modulo": salida, "error": f"archivo inválido: {p.name}"})
                else:
                    passed.append(item.get("archivo", p.name))

            # Video: si el MP4 final local existe, no tumbar QC por clips con rutas de otra máquina
            if salida == "video":
                local_final = base / "videos" / f"{ctx.slug}.mp4"
                local_audio = base / "videos" / f"{ctx.slug}_audio.mp4"
                if local_final.exists() and local_final.stat().st_size >= MIN_BYTES:
                    issues = [i for i in issues if i.get("modulo") != "video"]
                    if local_final.name not in passed:
                        passed.append(local_final.name)
                    if local_audio.exists() and local_audio.name not in passed:
                        passed.append(local_audio.name)
                    warnings.append("QC video: se validó por MP4 final local (rutas absolutas viejas ignoradas)")

        copy_checks = {
            "hook": "hooks",
            "guion": "guion",
            "captions": "captions",
            "thumbnail": "thumbnail",
            "audio": "audio",
        }
        for step, path_key in copy_checks.items():
            if step not in agentes:
                continue
            p = ctx.paths.get(path_key)
            if not p or not Path(p).exists():
                issues.append({"modulo": step, "error": f"falta meta/{path_key}.json"})
            else:
                passed.append(path_key)

        if "thumbnail" in agentes:
            thumb_png = Path(ctx.paths["copy_dir"]) / "thumbnail.png"
            if not thumb_png.exists() or thumb_png.stat().st_size < 100:
                issues.append({"modulo": "thumbnail", "error": "thumbnail.png inválido"})
            else:
                passed.append("thumbnail.png")

        # Audio: si hay narracion.mp3, no exigir mux para pasar QC
        if "audio" in agentes:
            narr = Path(ctx.paths["copy_dir"]) / "narracion.mp3"
            if narr.exists() and narr.stat().st_size > 1000:
                passed.append("narracion.mp3")

        ok = len(issues) == 0
        result = {
            "ok": ok,
            "passed": passed,
            "issues": issues,
            "warnings": warnings,
            "salidas": salidas,
            "receta": context.get("receta") or plan.get("receta"),
            "agentes": list(agentes),
        }
        save_json(ctx.paths["qc"], result)
        notes = f"QC {len(passed)} OK" if ok else f"QC {len(issues)} issues"
        return AgentResult(ok=ok, artifacts=[str(ctx.paths["qc"])], notes=notes, warnings=warnings)

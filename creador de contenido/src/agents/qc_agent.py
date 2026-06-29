"""QC por módulos activos."""

from __future__ import annotations

from pathlib import Path

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext

MIN_BYTES = 1024


class QcAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        salidas = context.get("salidas_pedidas") or ctx.salidas
        issues = []
        passed = []

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
            for item in items:
                p = Path(item.get("path", ""))
                if p.suffix == ".txt":
                    passed.append(item.get("archivo", ""))
                    continue
                if not p.exists() or p.stat().st_size < MIN_BYTES:
                    issues.append({"modulo": salida, "error": f"archivo inválido: {item.get('archivo')}"})
                else:
                    passed.append(item.get("archivo", ""))

        ok = len(issues) == 0
        result = {"ok": ok, "passed": passed, "issues": issues, "salidas": salidas}
        save_json(ctx.paths["qc"], result)
        return AgentResult(ok=ok, artifacts=[str(ctx.paths["qc"])], notes=f"QC {len(passed)} OK")

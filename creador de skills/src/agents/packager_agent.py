"""Empaqueta e instala skill en ~/.cursor/skills/."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.config import SKILLS_HOME, load_json, save_json, META_DIR
from src.types import AgentResult, PipelineContext


class PackagerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        composed = load_json(ctx.paths["composed"], {})
        qc = load_json(ctx.paths["qc"], {})
        nombre = context["nombre"]

        out_dir = ctx.paths["output"]
        out_dir.mkdir(parents=True, exist_ok=True)

        skill_src = ctx.paths["skill_md"]
        skill_dst = out_dir / "SKILL.md"
        if skill_src.resolve() != skill_dst.resolve():
            shutil.copy2(skill_src, skill_dst)

        files = ["SKILL.md"]
        ref_src = ctx.paths.get("reference_md")
        if ref_src and ref_src.exists():
            shutil.copy2(ref_src, out_dir / "reference.md")
            files.append("reference.md")

        manifest = {
            "nombre": nombre,
            "tipo": context.get("tipo"),
            "proyecto": context.get("proyecto_destino"),
            "triggers": context.get("triggers"),
            "qc_ok": qc.get("ok"),
            "archivos": files,
            "empaquetado_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(out_dir / "manifest.json", manifest)

        installed = None
        if context.get("instalar", True):
            dest = SKILLS_HOME / nombre
            dest.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(out_dir / f, dest / f)
            installed = str(dest)

        reg_path = META_DIR / "skills_instaladas.json"
        reg = load_json(reg_path, {"skills": []}) or {"skills": []}
        reg["skills"] = [s for s in reg.get("skills", []) if s.get("nombre") != nombre]
        reg["skills"].append(
            {
                "nombre": nombre,
                "path": installed or str(out_dir),
                "proyecto": context.get("proyecto_destino"),
                "instalado_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        save_json(reg_path, reg)

        notes = skill_dst.name
        if installed:
            notes += f" → {installed}"
        return AgentResult(ok=True, artifacts=[str(skill_dst)], notes=notes)

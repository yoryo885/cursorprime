"""Copia entregables a carpeta clientes/."""

from __future__ import annotations

import shutil
from pathlib import Path

from src.config import CLIENTES_ROOT, load_json, slug_output


def bridge_a_cliente(slug: str, cliente: str, proyecto: str) -> dict:
    out = slug_output(slug)
    md = out / "MARKETING-AUDIT.md"
    if not md.exists():
        return {"ok": False, "error": f"No existe {md} — corre audit primero"}

    dest = CLIENTES_ROOT / cliente / "proyectos" / proyecto / "entregables" / "estrategia"
    dest.mkdir(parents=True, exist_ok=True)

    copied = []
    for name in ("MARKETING-AUDIT.md", "audit.json", "manifest.json", "MARKETING-REPORT.pdf"):
        src = out / name
        if src.exists():
            shutil.copy2(src, dest / name)
            copied.append(str(dest / name))

    brief_path = CLIENTES_ROOT / cliente / "proyectos" / proyecto / "CONTEXTO.md"
    if brief_path.exists():
        syn = load_json(out / "audit.json", {})
        line = f"\n| {slug} | audit pipeline | score {syn.get('overall_score')} | {md.name} |\n"
        text = brief_path.read_text(encoding="utf-8")
        if "## Log de ejecución" in text:
            text = text.replace("## Log de ejecución\n\n| Fecha", f"## Log de ejecución\n{line}| Fecha")
            brief_path.write_text(text, encoding="utf-8")

    return {"ok": True, "dest": str(dest), "copied": copied}

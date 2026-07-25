"""Lectura solo-lectura de resumen/guía para hooks y guion (no modifica PDFs)."""

from __future__ import annotations

from pathlib import Path

from src.config import ROOT


def load_fuente_texto(path_str: str) -> str:
    candidates = [
        Path(path_str),
        ROOT / path_str,
        ROOT.parent / path_str.lstrip("./"),
        ROOT.parent / path_str.replace("../", "", 1),
    ]
    path = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not path:
        return ""
    if path.suffix.lower() in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")[:4000]
    return ""


def ideas_from_guia(guia: dict, fuente_texto: str) -> list[str]:
    ideas = list(guia.get("ideas") or guia.get("puntos") or [])
    if ideas:
        return [str(x) for x in ideas[:5]]
    if fuente_texto:
        lines: list[str] = []
        in_ideas = False
        for ln in fuente_texto.splitlines():
            if "ideas del pdf" in ln.lower():
                in_ideas = True
                continue
            if in_ideas and ln.startswith("##"):
                break
            if in_ideas and ln.strip().startswith(">"):
                lines.append(ln.strip().lstrip("> ").strip())
        if lines:
            return [x for x in lines if 30 < len(x) < 200][:5]
        raw = [ln.strip("-*# ").strip() for ln in fuente_texto.splitlines() if ln.strip()]
        bullets = [ln for ln in raw if 20 < len(ln) < 160][:5]
        if bullets:
            return bullets
    temas = guia.get("temas") or []
    return [str(t) for t in temas[:5]] or []

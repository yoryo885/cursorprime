"""Lector solo-lectura de resúmenes/PDF (no toca libros a entender)."""

from __future__ import annotations

import re
from pathlib import Path


def resolve_fuente(path_str: str) -> Path | None:
    if not path_str:
        return None
    raw = Path(path_str).expanduser()
    candidates = [raw]
    if not raw.is_absolute():
        root = Path(__file__).resolve().parent.parent
        candidates.extend(
            [
                root / path_str,
                root.parent / path_str,
                Path.cwd() / path_str,
            ]
        )
    for p in candidates:
        if p.exists() and p.is_file():
            return p.resolve()
    return None


def _read_text(path: Path) -> str:
    if path.suffix.lower() in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            return ""
    return ""


def _ideas_from_markdown(text: str) -> list[str]:
    """Prioriza bloques «Ideas del PDF» / citas > ; fallback headers + frases fuertes."""
    ideas: list[str] = []
    # Citas bajo Ideas del PDF
    for m in re.finditer(
        r"(?:###?\s*Ideas del PDF|Ideas del PDF)([\s\S]*?)(?=\n---|\n##\s|\Z)",
        text,
        flags=re.I,
    ):
        block = m.group(1)
        for q in re.findall(r">\s*(.+)", block):
            line = q.strip()
            if 40 <= len(line) <= 280:
                ideas.append(line)
    if ideas:
        return _dedupe(ideas)[:7]

    # Bullets / numeradas
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^(\d+\.|[-*])\s+", s):
            s = re.sub(r"^(\d+\.|[-*])\s+", "", s).strip()
            if 40 <= len(s) <= 220:
                ideas.append(s)
    if ideas:
        return _dedupe(ideas)[:7]

    # Fallback: párrafos cortos bajo ## 
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for p in paras:
        if p.startswith("#") or p.startswith("!["):
            continue
        one = " ".join(p.split())
        if 60 <= len(one) <= 220 and not one.startswith("**Fecha"):
            ideas.append(one)
        if len(ideas) >= 5:
            break
    return _dedupe(ideas)[:7]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for i in items:
        key = i.lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(i)
    return out


def _titulo_from_text(text: str, path: Path) -> str:
    for line in text.splitlines()[:15]:
        if line.startswith("# "):
            t = line[2:].strip()
            t = re.sub(r"^Resumen:\s*", "", t, flags=re.I)
            return t[:120]
    return path.stem.replace("_", " ")[:120]


def extract_ideas(path_str: str) -> dict:
    """
    Pesca ideas centrales de una fuente existente.
    Nunca escribe en la fuente. Solo lectura.
    """
    path = resolve_fuente(path_str)
    if not path:
        return {
            "fuente_path": path_str or "",
            "titulo_fuente": "",
            "ideas_centrales": [],
            "extracto_corto": "",
            "modo": "solo_lectura",
            "confidence": "low",
            "ok": False,
            "nota": "Fuente no encontrada (se continúa solo con --tema)",
        }

    text = _read_text(path)
    ideas = _ideas_from_markdown(text) if text else []
    titulo = _titulo_from_text(text, path) if text else path.stem
    extracto = " | ".join(ideas[:3])

    return {
        "fuente_path": str(path),
        "titulo_fuente": titulo,
        "ideas_centrales": ideas,
        "extracto_corto": extracto,
        "modo": "solo_lectura",
        "confidence": "medium" if ideas else "low",
        "ok": bool(ideas),
        "nota": "No se modifica el PDF ni el markdown fuente",
    }

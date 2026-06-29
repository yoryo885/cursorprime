from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


KDP_PROHIBIDAS = (
    "el mejor",
    "la mejor",
    "número uno",
    "numero uno",
    "#1",
    "gratis",
    "free",
    "guaranteed",
    "garantizado",
)


def parse_json_response(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group())
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def sanitize_kdp_text(texto: str) -> str:
    out = (texto or "").strip()
    for palabra in KDP_PROHIBIDAS:
        out = re.sub(re.escape(palabra), "", out, flags=re.IGNORECASE)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def load_contexto_cercano(pdf_path: Path) -> dict[str, Any]:
    """Carga contexto_usuario.json o producto.json si están junto al PDF."""
    base = pdf_path.parent
    ctx: dict[str, Any] = {}
    for name in ("contexto_usuario.json",):
        p = base / name
        if p.is_file():
            try:
                ctx.update(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
    producto = base / "meta" / "producto.json"
    if producto.is_file():
        try:
            ctx["producto"] = json.loads(producto.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return ctx


def format_extra_instructions(instrucciones: list[str] | None) -> str:
    if not instrucciones:
        return ""
    lineas = "\n".join(f"- {i}" for i in instrucciones if i.strip())
    if not lineas:
        return ""
    return f"\nMEJORAS APRENDIDAS (aplicar en esta generación):\n{lineas}\n"


def kdp_output_dir(pdf_path: Path) -> Path:
    return pdf_path.parent / "kdp"


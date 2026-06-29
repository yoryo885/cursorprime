"""Puente análisis → creador de contenido (3 PNG + 1 GIF)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from src.config import ANALISIS_ROOT, CURSORPRIME_ROOT, load_json, save_json, slugify

CONTENIDO_ROOT = CURSORPRIME_ROOT / "creador de contenido"
CONTENIDO_CLI = CONTENIDO_ROOT / "creador_imagenes_main.py"


def _analisis_file(analisis_slug: str) -> Path:
    return ANALISIS_ROOT / "data" / analisis_slug / "meta" / "analisis.json"


def _temas_desde_analisis(analisis: dict) -> list[str]:
    productos = analisis.get("productos_que_funcionan") or []
    temas: list[str] = []
    for p in productos[:3]:
        t = slugify(p.replace("/", " ").split("(")[0])[:24]
        if t and t not in temas:
            temas.append(t.replace("_", "-"))
    if len(temas) < 3:
        for op in analisis.get("oportunidades_pipeline") or []:
            t = slugify(str(op.get("titulo") or ""))[:24].replace("_", "-")
            if t and t not in temas:
                temas.append(t)
    while len(temas) < 3:
        temas.append(f"tema-{len(temas)+1}")
    return temas[:3]


def run_pack_visual(analisis_slug: str, pack_slug: str | None = None) -> bool:
    analisis_path = _analisis_file(analisis_slug)
    if not analisis_path.exists():
        print(f"❌ No hay análisis: {analisis_path}")
        return False

    analisis = load_json(analisis_path, {}) or {}
    slug = pack_slug or f"pack_{slugify(analisis_slug)}"
    temas = _temas_desde_analisis(analisis)

    lote = {
        "titulo": f"Pack promocional — {analisis.get('tema', analisis_slug)}",
        "salidas": ["png", "gif"],
        "estilo": "yordy-minimal",
        "temas": temas,
        "gif": {"frames": 4, "duration_ms": 300},
        "origen": {
            "pipeline": "lluvia-de-ideas",
            "analisis_slug": analisis_slug,
            "idea_id": "idea-4f897bfa",
        },
        "notas": "Generado automáticamente post-investigación (3 PNG + GIF por tema)",
    }

    lote_dir = CONTENIDO_ROOT / "data" / slug / "inputs"
    lote_dir.mkdir(parents=True, exist_ok=True)
    lote_path = lote_dir / "lote.json"
    save_json(lote_path, lote)

    print(f"\n🎨 Pack visual — {slug}")
    print(f"   Temas: {', '.join(temas)}")
    print(f"   Lote: {lote_path}\n")

    if not CONTENIDO_CLI.exists():
        print(f"❌ No encontrado: {CONTENIDO_CLI}")
        return False

    cmd = [sys.executable, str(CONTENIDO_CLI), "--slug", slug, "--modo", "all"]
    print(f"   → {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(CONTENIDO_ROOT))
    if result.returncode == 0:
        print(f"\n✅ Pack: creador de contenido/data/{slug}/\n")
    return result.returncode == 0

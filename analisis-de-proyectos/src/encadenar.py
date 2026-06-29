"""Encadena analizar → lluvia → evaluar tras exportar idea."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from src.bridge_proyectos import exportar_a_proyectos
from src.config import CURSORPRIME_ROOT, IDEAS_FROM_ANALISIS, IDEAS_ROOT, load_json


LLUVIA_ROOT = CURSORPRIME_ROOT / "lluvia-de-ideas"


def _idea_path(analisis_slug: str) -> Path | None:
    for p in IDEAS_FROM_ANALISIS.glob("*.json"):
        d = load_json(p, {}) or {}
        if d.get("analisis_slug") == analisis_slug:
            return p
    return None


def encadenar(
    analisis_slug: str,
    *,
    exportar: bool = True,
    lluvia: bool = True,
    evaluar: bool = True,
    reset: bool = False,
) -> dict:
    """
    1. Exportar idea → ideas/from-analisis/ (si exportar=True)
    2. Lluvia de ideas desde el análisis
    3. Evaluar la idea exportada
    """
    pasos: list[dict] = []
    idea_path: Path | None = None
    idea_slug: str | None = None

    if exportar:
        r = exportar_a_proyectos(analisis_slug)
        if not r.get("ok"):
            return {"ok": False, "analisis_slug": analisis_slug, "error": r.get("error"), "pasos": pasos}
        idea_path = Path(r["path"])
        idea_slug = r["slug"]
        pasos.append({"paso": "exportar", "ok": True, "path": str(idea_path), "slug": idea_slug})
        print(f"\n🔗 Encadenar — {analisis_slug}")
        print(f"   1/3 Exportado → {idea_path.name}")
    else:
        idea_path = _idea_path(analisis_slug)
        if not idea_path:
            return {
                "ok": False,
                "analisis_slug": analisis_slug,
                "error": f"No hay idea en from-analisis para {analisis_slug}. Usa --exportar primero.",
                "pasos": pasos,
            }
        idea_slug = (load_json(idea_path, {}) or {}).get("slug") or idea_path.stem
        print(f"\n🔗 Encadenar — {analisis_slug} (idea ya exportada)")

    if lluvia:
        cmd = [sys.executable, "lluvia_main.py", "lluvia", "--desde-analisis", analisis_slug]
        if reset:
            cmd.append("--reset-checkpoint")
        print(f"   2/3 Lluvia ← {analisis_slug}")
        rc = subprocess.run(cmd, cwd=str(LLUVIA_ROOT)).returncode
        ok_lluvia = rc == 0
        pasos.append({"paso": "lluvia", "ok": ok_lluvia, "slug": f"lluvia_{analisis_slug}"})
        if not ok_lluvia:
            print("   ⚠ Lluvia falló — se continúa con evaluar")

    if evaluar and idea_path:
        rel = f"ideas/from-analisis/{idea_path.name}"
        cmd = [sys.executable, "evaluar.py", rel]
        print(f"   3/3 Evaluar → {rel}")
        rc = subprocess.run(cmd, cwd=str(IDEAS_ROOT)).returncode
        ver_path = IDEAS_ROOT / "evaluaciones" / idea_slug / "veredicto.json"
        ver = load_json(ver_path, {}) or {}
        ok_eval = rc == 0 and bool(ver)
        pasos.append(
            {
                "paso": "evaluar",
                "ok": ok_eval,
                "veredicto": ver.get("veredicto"),
                "score": ver.get("score"),
                "path": str(ver_path),
            }
        )
        if ok_eval:
            print(f"   ✅ {ver.get('veredicto', '?').upper()} {ver.get('score')}/100 → evaluaciones/{idea_slug}/")

    ok = all(p.get("ok") for p in pasos if p["paso"] != "lluvia" or lluvia) if pasos else False
    # evaluar + exportar must succeed; lluvia optional for overall ok if it failed
    critical = [p for p in pasos if p["paso"] in ("exportar", "evaluar")]
    ok = bool(critical) and all(p.get("ok") for p in critical)

    return {
        "ok": ok,
        "analisis_slug": analisis_slug,
        "idea_slug": idea_slug,
        "pasos": pasos,
    }

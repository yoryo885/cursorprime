"""Puente ideas aprobadas → ideas de proyectos (+ evaluar opcional)."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import CURSORPRIME_ROOT, load_json, save_json, slugify

IDEAS_ROOT = CURSORPRIME_ROOT / "ideas de proyectos"
IDEAS_DIR = IDEAS_ROOT / "ideas"
FROM_LLUVIA = IDEAS_DIR / "from-lluvia"
EVALUAR_CLI = IDEAS_ROOT / "evaluar.py"


def idea_a_json(idea: dict) -> dict:
    titulo = idea.get("titulo") or "Idea sin título"
    slug = slugify(titulo)
    return {
        "titulo": titulo,
        "slug": slug,
        "tipo": "from_lluvia",
        "categoria_lluvia": idea.get("categoria"),
        "origen_idea_id": idea.get("id"),
        "problema": idea.get("problema") or "",
        "propuesta": idea.get("propuesta") or "",
        "proyecto_destino": idea.get("proyecto_afectado") or "general",
        "confidence_lluvia": idea.get("confidence"),
        "aprobada_at": idea.get("aprobada_at"),
        "hipotesis": [
            idea.get("propuesta") or "Validar con MVP mínimo",
        ],
        "notas": f"Exportada desde lluvia-de-ideas cola ({idea.get('id')})",
    }


def exportar_idea(idea: dict, evaluar: bool = False) -> dict:
    payload = idea_a_json(idea)
    slug = payload["slug"]
    FROM_LLUVIA.mkdir(parents=True, exist_ok=True)
    out_path = FROM_LLUVIA / f"{slug}.json"
    save_json(out_path, payload)

    result = {"ok": True, "path": str(out_path), "slug": slug, "evaluacion": None}

    if evaluar and EVALUAR_CLI.exists() and idea.get("categoria") == "nuevo_proyecto":
        cmd = [sys.executable, str(EVALUAR_CLI), str(out_path)]
        proc = subprocess.run(cmd, cwd=str(IDEAS_ROOT), capture_output=True, text=True)
        result["evaluacion"] = {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout[-500:] if proc.stdout else "",
        }

    return result


def exportar_aprobadas(evaluar_nuevo_proyecto: bool = False) -> list[dict]:
    aprobadas_dir = Path(__file__).resolve().parent.parent / "cola" / "aprobadas"
    results = []
    for p in sorted(aprobadas_dir.glob("idea-*.json")):
        idea = load_json(p, {}) or {}
        if idea.get("estado") != "aprobada" and idea.get("estado") != "implementada":
            continue
        r = exportar_idea(
            idea,
            evaluar=evaluar_nuevo_proyecto and idea.get("categoria") == "nuevo_proyecto",
        )
        results.append(r)
    return results


def marcar_implementada(idea_id: str, notas: str = "") -> None:
    aprobadas_dir = Path(__file__).resolve().parent.parent / "cola" / "aprobadas"
    path = aprobadas_dir / f"{idea_id}.json"
    if not path.exists():
        return
    idea = load_json(path, {}) or {}
    idea["estado"] = "implementada"
    idea["implementada_at"] = datetime.now(timezone.utc).isoformat()
    if notas:
        idea["implementacion_notas"] = notas
    save_json(path, idea)

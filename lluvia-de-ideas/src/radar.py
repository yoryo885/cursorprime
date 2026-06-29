"""Radar semanal — investigación KDP programable."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import META_DIR, load_json, save_json, slugify
from src.pipeline_investigacion import run_investigacion


def semana_actual() -> str:
    y, w, _ = datetime.now(timezone.utc).isocalendar()
    return f"{y}w{w:02d}"


def radar_slug(semana: str | None = None) -> str:
    return f"radar-{semana or semana_actual()}"


def cargar_brief_radar() -> dict:
    cfg = load_json(META_DIR / "radar_kdp.json", {}) or {}
    return {
        "tema": cfg.get("tema") or "nichos kdp",
        "titulo": cfg.get("nombre") or "Radar KDP",
        "queries": cfg.get("queries") or [],
        "fuentes": cfg.get("fuentes") or ["youtube", "web"],
        "tipo": "radar_semanal",
    }


def registrar_historial(slug: str, ok: bool) -> None:
    log_path = META_DIR.parent / "logs" / "radar_historial.json"
    hist = load_json(log_path, []) or []
    hist.append(
        {
            "slug": slug,
            "semana": slug.replace("radar-", ""),
            "ok": ok,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_json(log_path, hist[-52:])  # último año aprox


def run_radar(semana: str | None = None, reset: bool = False) -> bool:
    slug = radar_slug(semana)
    brief = cargar_brief_radar()
    print(f"\n📡 Radar KDP — semana {slug.replace('radar-', '')}\n")
    ok = run_investigacion(slug=slug, brief=brief, reset=reset)
    registrar_historial(slug, ok)
    if ok:
        print(f"   Historial: logs/radar_historial.json")
    return ok

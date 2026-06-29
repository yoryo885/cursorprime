"""Radar semanal automático — corre una vez por semana, fetch live."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.bridge_proyectos import exportar_a_proyectos
from src.config import META_DIR, load_json, save_json, slug_output
from src.encadenar import encadenar
from src.radar import cargar_brief_radar, radar_slug, registrar_historial, run_radar, semana_actual


def _estado_path() -> Path:
    return META_DIR / "radar_auto_state.json"


def ya_corrio_esta_semana(semana: str) -> bool:
    state = load_json(_estado_path(), {}) or {}
    return state.get("ultima_semana_ok") == semana


def marcar_corregido(semana: str, slug: str, ok: bool, export_path: str | None = None) -> None:
    save_json(
        _estado_path(),
        {
            "ultima_semana_ok": semana if ok else load_json(_estado_path(), {}).get("ultima_semana_ok"),
            "ultima_corrida": {
                "semana": semana,
                "slug": slug,
                "ok": ok,
                "at": datetime.now(timezone.utc).isoformat(),
                "exportado": export_path,
            },
        },
    )


def run_radar_auto(
    semana: str | None = None,
    *,
    force: bool = False,
    exportar: bool | None = None,
    encadenar: bool = False,
    reset: bool = False,
) -> dict:
    """
    Radar con fetch live. Salta si ya corrió OK esta semana (salvo --force).
    Exporta a ideas/from-analisis/ si radar_kdp.json tiene auto_exportar: true.
    """
    sem = semana or semana_actual()
    slug = radar_slug(sem)
    cfg = load_json(META_DIR / "radar_kdp.json", {}) or {}
    do_export = exportar if exportar is not None else bool(cfg.get("auto_exportar", True))

    if not force and ya_corrio_esta_semana(sem):
        out_md = slug_output(slug) / "analisis.md"
        if out_md.exists():
            return {
                "ok": True,
                "skipped": True,
                "mensaje": f"Radar {sem} ya corrido esta semana. Usa --force para repetir.",
                "slug": slug,
            }

    print(f"\n📡 Radar automático — semana {sem} · fetch LIVE\n")
    ok = run_radar(semana=sem, reset=reset)
    export_path = None

    if ok and do_export:
        r = exportar_a_proyectos(slug)
        if r.get("ok"):
            export_path = r.get("path")
            print(f"   📤 Idea exportada: {export_path}")

    chain_result = None
    if ok and encadenar:
        chain_result = encadenar(slug, exportar=not bool(export_path), reset=reset)

    marcar_corregido(sem, slug, ok, export_path)
    return {
        "ok": ok and (chain_result is None or chain_result.get("ok", True)),
        "skipped": False,
        "slug": slug,
        "semana": sem,
        "exportado": export_path,
        "encadenado": chain_result,
        "mensaje": "Radar completado" if ok else "Radar falló — revisa fetch o logs",
    }

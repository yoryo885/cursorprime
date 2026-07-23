"""Orquestador — TikTok content pipeline."""

from __future__ import annotations

import importlib.util
import traceback
from datetime import datetime, timezone
from typing import Any

from src.config import (
    AGENT_ORDER,
    LOGS_DIR,
    ROOT,
    checkpoint_path,
    load_json,
    output_dir,
    save_json,
    slugify,
)

AGENTS_DIR = ROOT / "src" / "agents"


def _load_agent(agent_id: str):
    path = AGENTS_DIR / f"{agent_id}.py"
    if not path.exists():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location(f"tiktok_agent_{agent_id}", path)
    if spec is None or spec.loader is None:
        raise ImportError(agent_id)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "run"):
        raise AttributeError(f"{agent_id} sin def run")
    return mod.run


def _log_mejora(slug: str, step: str, notes: str = "") -> None:
    path = LOGS_DIR / "mejoras.json"
    entries = load_json(path, []) or []
    entries.append(
        {
            "slug": slug,
            "step": step,
            "notes": notes,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_json(path, entries)


def _log_error(slug: str, step: str, error: str) -> None:
    path = LOGS_DIR / "errores.json"
    entries = load_json(path, []) or []
    entries.append(
        {
            "slug": slug,
            "step": step,
            "error": error,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_json(path, entries)


def _save_checkpoint(slug: str, last: str, state: dict) -> None:
    save_json(
        checkpoint_path(slug),
        {
            "slug": slug,
            "last_completed": last,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "keys": list(state.keys()),
        },
    )


def run_pipeline(
    tema: str,
    *,
    slug: str | None = None,
    nicho: str = "productividad",
    producto: str = "",
    fuente: str = "",
    reset: bool = False,
    solo: str | None = None,
    desde: str | None = None,
) -> dict[str, Any]:
    slug = slugify(slug or tema)
    out = output_dir(slug)
    out.mkdir(parents=True, exist_ok=True)

    state_path = out / "guion.json"
    if reset or not state_path.exists():
        state: dict[str, Any] = {
            "tema": tema,
            "nicho": nicho,
            "producto": producto or tema,
            "slug": slug,
            "fuente": fuente,
        }
    else:
        state = load_json(state_path, {}) or {
            "tema": tema,
            "nicho": nicho,
            "producto": producto or tema,
            "slug": slug,
        }
        state["tema"] = tema
        state["nicho"] = nicho
        if fuente:
            state["fuente"] = fuente

    state["_shotlist_path"] = str(out / "shotlist.md")
    if fuente:
        state["fuente"] = fuente

    if solo:
        steps = [solo]
    else:
        steps = list(AGENT_ORDER)
        if desde and desde in steps:
            steps = steps[steps.index(desde) :]

    ckpt = load_json(checkpoint_path(slug), {}) or {}
    last_done = ckpt.get("last_completed") if not reset and not solo and not desde else None
    if last_done and last_done in AGENT_ORDER and not solo and not desde:
        idx = AGENT_ORDER.index(last_done) + 1
        steps = AGENT_ORDER[idx:]

    print(f"\n🎬 TikTok Pipeline — {slug}")
    print(f"   Tema: {tema} · pasos: {len(steps)}\n")

    for agent_id in steps:
        print(f"  → {agent_id}")
        try:
            run_fn = _load_agent(agent_id)
            result = run_fn(state)
            if not isinstance(result, dict):
                raise RuntimeError(f"{agent_id} no devolvió dict")
            state.update(result)
            # Tras pescar la fuente: enriquecer tema sin tocar el PDF
            if agent_id == "00_extract_fuente":
                if result.get("tema_desde_fuente") and (
                    not state.get("tema") or state.get("tema") in {"desde_fuente", "productividad"}
                ):
                    state["tema"] = result["tema_desde_fuente"]
            _log_mejora(slug, agent_id, notes="ok")
            _save_checkpoint(slug, agent_id, state)
            persist = {k: v for k, v in state.items() if not k.startswith("_")}
            save_json(state_path, persist)
        except Exception as exc:
            _log_error(slug, agent_id, f"{exc}\n{traceback.format_exc()}")
            print(f"      ✗ {exc}")
            raise

    persist = {k: v for k, v in state.items() if not k.startswith("_")}
    save_json(state_path, persist)

    shotlist = out / "shotlist.md"
    if state.get("shotlist_md"):
        shotlist.write_text(state["shotlist_md"], encoding="utf-8")

    qa_path = out / "qa_report.json"
    save_json(qa_path, state.get("qa") or {})

    print(f"\n✅ Listo: output/{slug}/")
    print("   guion.json · shotlist.md · qa_report.json\n")
    return state

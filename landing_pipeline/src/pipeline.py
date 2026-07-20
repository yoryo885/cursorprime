"""Orquestador: agentes 01→13 con reintento por paso."""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from src.agents import (
    a01_brief,
    a02_hero,
    a03_social_proof,
    a04_problem,
    a05_benefits,
    a06_testimonials,
    a07_pricing,
    a08_faq,
    a09_cta_final,
    a10_footer,
    a11_design,
    a12_qa,
    a13_visual_qa,
)
from src.llm_client import LLMClient
from src.paths import LOGS, ensure_slug

AGENTS: list[tuple[str, Callable[[dict], dict]]] = [
    ("01_brief", a01_brief.run),
    ("02_hero", a02_hero.run),
    ("03_social_proof", a03_social_proof.run),
    ("04_problem", a04_problem.run),
    ("05_benefits", a05_benefits.run),
    ("06_testimonials", a06_testimonials.run),
    ("07_pricing", a07_pricing.run),
    ("08_faq", a08_faq.run),
    ("09_cta_final", a09_cta_final.run),
    ("10_footer", a10_footer.run),
    ("11_design", a11_design.run),
    ("12_qa", a12_qa.run),
    ("13_visual_qa", a13_visual_qa.run),
]

COPY_KEYS = {
    "02_hero": "hero",
    "03_social_proof": "social_proof",
    "04_problem": "problem",
    "05_benefits": "benefits",
    "06_testimonials": "testimonials",
    "07_pricing": "pricing",
    "08_faq": "faq",
    "09_cta_final": "cta_final",
    "10_footer": "footer",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_mejora(mensaje: str, cambio: str) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    path = LOGS / "mejoras.json"
    if path.exists() and path.stat().st_size:
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "mejoras": []}
    n = len(data.get("mejoras") or []) + 1
    data.setdefault("mejoras", []).append(
        {"id": f"m{n:03d}", "at": _now(), "mensaje": mensaje, "cambio": cambio, "aplicado": True}
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _save(path: Path, obj: Any) -> None:
    if isinstance(obj, str):
        path.write_text(obj, encoding="utf-8")
    else:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_pipeline(
    negocio: dict[str, Any],
    *,
    llm: LLMClient | None = None,
    solo: str | None = None,
    retry_from: str | None = None,
) -> dict[str, Any]:
    llm = llm or LLMClient()
    slug = (negocio.get("slug") or "demo").strip()
    out = ensure_slug(slug)
    (out / "screenshots").mkdir(parents=True, exist_ok=True)
    checkpoint = out / "checkpoint.json"
    state: dict[str, Any] = {
        "brief": {},
        "copy": {},
        "html": "",
        "qa": {},
        "visual_qa": {},
        "done": [],
    }
    if checkpoint.exists():
        prev = json.loads(checkpoint.read_text(encoding="utf-8"))
        state.update({k: prev[k] for k in state if k in prev})
        # recargar html desde disco si hay checkpoint
        html_file = out / "landing.html"
        if html_file.exists() and not state.get("html"):
            state["html"] = html_file.read_text(encoding="utf-8")
        brief_file = out / "brief.json"
        if brief_file.exists() and not state.get("brief"):
            state["brief"] = json.loads(brief_file.read_text(encoding="utf-8"))
        copy_file = out / "copy.json"
        if copy_file.exists() and not state.get("copy"):
            state["copy"] = json.loads(copy_file.read_text(encoding="utf-8"))

    start = False if retry_from or solo else True
    results: dict[str, Any] = {}

    for agent_id, fn in AGENTS:
        if solo and agent_id != solo:
            continue
        if retry_from and not start:
            if agent_id == retry_from:
                start = True
            else:
                continue

        print(f"  → {agent_id}")
        try:
            payload: dict[str, Any] = {
                "llm": llm,
                "brief": state.get("brief") or {},
                "copy": state.get("copy") or {},
                "html": state.get("html") or "",
                "html_path": str(out / "landing.html"),
                "out_dir": str(out),
            }
            if agent_id == "01_brief":
                brief = fn(dict(negocio))
                state["brief"] = brief
                _save(out / "brief.json", brief)
                results[agent_id] = brief
            elif agent_id == "11_design":
                design = fn(payload)
                html = design["html"]
                state["html"] = html
                _save(out / "landing.html", html)
                results[agent_id] = {"ok": True, "bytes": len(html)}
            elif agent_id == "12_qa":
                qa = fn(payload)
                state["qa"] = qa
                results[agent_id] = qa
            elif agent_id == "13_visual_qa":
                visual = fn(payload)
                state["visual_qa"] = visual
                # merge into qa_report
                qa = dict(state.get("qa") or {})
                qa["visual_qa"] = visual
                if visual.get("overlaps"):
                    qa.setdefault("criticos", []).append(
                        {
                            "tipo": "overlap_visual",
                            "detalle": f"Overlap real entre secciones: {visual['overlaps']}",
                            "texto": str(visual["overlaps"]),
                        }
                    )
                    qa["bugs_v2"] = dict(qa.get("bugs_v2") or {})
                    qa["bugs_v2"]["overlap_secciones"] = "fail"
                    qa["score"] = max(0, int(qa.get("score") or 100) - 20)
                state["qa"] = qa
                _save(out / "qa_report.json", qa)
                results[agent_id] = visual
            else:
                block = fn(payload)
                key = COPY_KEYS[agent_id]
                state.setdefault("copy", {})[key] = block
                _save(out / "copy.json", state["copy"])
                results[agent_id] = block

            if agent_id == "12_qa":
                _save(out / "qa_report.json", state["qa"])

            if agent_id not in state["done"]:
                state["done"].append(agent_id)
            _save(
                checkpoint,
                {
                    "brief": state.get("brief"),
                    "copy": state.get("copy"),
                    "qa": state.get("qa"),
                    "visual_qa": state.get("visual_qa"),
                    "done": state.get("done"),
                    "html_saved": bool(state.get("html")),
                },
            )
        except Exception as e:
            err = {"agent": agent_id, "error": str(e), "trace": traceback.format_exc(), "at": _now()}
            _save(out / "error.json", err)
            print(f"  ✗ {agent_id}: {e}")
            print(f"    Reintentá: python3 landing_main.py run --slug {slug} --retry-from {agent_id}")
            raise

    _log_mejora(
        f"pipeline run slug={slug}",
        f"agentes={','.join(state.get('done') or [])} mock={llm.mock}",
    )
    return {
        "slug": slug,
        "out": str(out),
        "brief": state.get("brief"),
        "copy": state.get("copy"),
        "qa": state.get("qa"),
        "visual_qa": state.get("visual_qa"),
        "landing": str(out / "landing.html"),
        "results": results,
    }

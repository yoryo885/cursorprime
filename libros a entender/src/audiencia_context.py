"""Carga audiencia/oficio del plan y genera instrucciones para resúmenes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def load_audiencia_context(output_dir: Path) -> dict[str, str]:
    output_dir = Path(output_dir)
    ctx: dict[str, str] = {
        "audiencia": "",
        "reto": "",
        "intento_fallido": "",
    }

    contexto_path = output_dir / "contexto_usuario.json"
    try:
        data = json.loads(contexto_path.read_text(encoding="utf-8"))
        ctx["audiencia"] = str(data.get("audiencia", "") or "").strip()
        ctx["reto"] = str(data.get("reto", "") or "").strip()
        ctx["intento_fallido"] = str(data.get("intento_fallido", "") or "").strip()
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    if not ctx["audiencia"]:
        try:
            from src.agents.planner_agent import BookPlan, plan_path_for

            plan = BookPlan.from_dict(
                json.loads(plan_path_for(output_dir).read_text(encoding="utf-8"))
            )
            ctx["audiencia"] = (
                plan.audiencia
                or plan.contexto_usuario.get("audiencia", "")
                or plan.contexto_usuario.get("ocupacion", "")
            ).strip()
            if not ctx["reto"]:
                ctx["reto"] = str(plan.contexto_usuario.get("reto", "") or "")
            if not ctx["intento_fallido"]:
                ctx["intento_fallido"] = str(
                    plan.contexto_usuario.get("intento_fallido", "") or ""
                )
        except (FileNotFoundError, json.JSONDecodeError, OSError, ImportError):
            pass

    return ctx


def build_resumen_audiencia_instructions(
    ctx: dict[str, str],
    output_dir: Optional[Path] = None,
) -> str:
    from src.rol_usuario import build_rol_block, build_rol_profile, ensure_rol_perfil

    audiencia = (ctx.get("audiencia") or "").strip()
    if not audiencia:
        return ""

    profile = None
    if output_dir is not None:
        profile = ensure_rol_perfil(Path(output_dir))
    if profile is None:
        profile = build_rol_profile(
            audiencia,
            reto=ctx.get("reto", ""),
            intento_fallido=ctx.get("intento_fallido", ""),
        )

    block = build_rol_block(profile, agent="resumen")
    voz = (
        f"\n**VOZ:** segunda persona directa (tú, tu, tus). "
        f"Habla al lector como {audiencia}. Prohibido yo/mi/me."
    )
    return block + voz

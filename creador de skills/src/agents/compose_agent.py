"""Agente 3: compone SKILL.md (+ reference opcional)."""

from __future__ import annotations

from src.config import load_json, save_json
from src.types import AgentResult, PipelineContext


def _bullets(items: list) -> str:
    if not items:
        return "- (definir en iteración)"
    return "\n".join(f"- {x}" for x in items)


def _pasos_section(pasos: list) -> str:
    if not pasos:
        return "1. Analizar solicitud\n2. Ejecutar proceso\n3. Validar salida\n4. Entregar artefactos"
    lines = []
    for i, p in enumerate(pasos, 1):
        if isinstance(p, dict):
            lines.append(f"{i}. **{p.get('titulo', f'Paso {i}')}**: {p.get('detalle', '')}")
        else:
            lines.append(f"{i}. {p}")
    return "\n".join(lines)


class ComposeAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        plantilla = load_json(ctx.paths["plantilla"], {})
        nombre = context["nombre"]
        triggers = context.get("triggers") or []
        trigger_text = ", ".join(triggers) if triggers else nombre.replace("-", " ")

        desc_tpl = plantilla.get("description_template", "")
        description = desc_tpl.format(
            titulo=context.get("titulo", nombre),
            proyecto=context.get("proyecto_nombre", ""),
            triggers=trigger_text,
            proceso=(context.get("proceso") or "")[:200],
        ).strip()

        body_tpl = plantilla.get("body_template", "# {titulo}\n\n{proceso}")
        body = body_tpl.format(
            titulo=context.get("titulo", nombre),
            nombre=nombre,
            proyecto=context.get("proyecto_nombre", ""),
            proyecto_carpeta=context.get("proyecto_carpeta", ""),
            proceso=context.get("proceso", ""),
            pasos=_pasos_section(context.get("pasos", [])),
            reglas=_bullets(context.get("reglas", [])),
            triggers=trigger_text,
        )

        frontmatter = (
            "---\n"
            f"name: {nombre}\n"
            f"description: >-\n  {description.replace(chr(10), ' ')}\n"
            "---\n\n"
        )
        skill_md = frontmatter + body.strip() + "\n"

        out_skill = ctx.paths["skill_md"]
        out_skill.parent.mkdir(parents=True, exist_ok=True)
        out_skill.write_text(skill_md, encoding="utf-8")

        artifacts = [str(out_skill)]
        line_count = len(skill_md.splitlines())

        ref_path = ctx.paths.get("reference_md")
        if context.get("incluir_reference") and ref_path:
            ref = plantilla.get("reference_template", "## Referencia\n\n{proceso}").format(
                titulo=context.get("titulo"),
                proceso=context.get("proceso", ""),
                pasos=_pasos_section(context.get("pasos", [])),
            )
            ref_path.write_text(ref.strip() + "\n", encoding="utf-8")
            artifacts.append(str(ref_path))

        meta = {
            "nombre": nombre,
            "description": description,
            "line_count": line_count,
            "tipo": context.get("tipo"),
            "triggers": triggers,
            "artifacts": artifacts,
        }
        save_json(ctx.paths["composed"], meta)
        return AgentResult(ok=True, artifacts=artifacts, notes=f"SKILL.md ({line_count} líneas)")

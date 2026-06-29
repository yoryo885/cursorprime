from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.models import TopicResult


class ContextAgent:
    @staticmethod
    def recopilar(
        slug: str,
        output_dir: Path,
        llm: Optional[Any] = None,
        resultados: list[TopicResult] | None = None,
    ) -> dict[str, Any]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "contexto_usuario.json"

        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        if llm is None:
            return {}

        if resultados is None:
            return {}

        textos = []
        for r in resultados:
            if r.fallo:
                continue
            texto = (r.resumen_voz or r.resumen).strip()
            if texto:
                textos.append(texto)

        texto_concatenado = "\n\n".join(textos)
        if not texto_concatenado:
            return {}

        prompt = f"""Este es un resumen personal escrito en primera persona por el lector \
de un libro. Basándote SOLO en lo que dice el texto, extrae en JSON:
- ocupacion: a qué se dedica o en qué contexto aplica los aprendizajes
- reto: cuál es su mayor problema o reto actual
- intento_fallido: qué intentó que no le funcionó

Usa sus propias palabras cuando puedas. Si no puedes inferir un campo \
con certeza, deja la cadena vacía. Responde SOLO el JSON.

Texto:
{texto_concatenado}"""

        raw = llm.call(prompt)
        data = ContextAgent._parse_contexto(raw)
        if not data.get("ocupacion"):
            ocupacion_cfg = ContextAgent._ocupacion_desde_config()
            if ocupacion_cfg:
                data["ocupacion"] = ocupacion_cfg
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return data

    @staticmethod
    def _ocupacion_desde_config() -> str:
        config_path = Path(__file__).resolve().parent.parent / "config" / "usuario.json"
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            return str(cfg.get("ocupacion", "") or "").strip()
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return ""

    @staticmethod
    def _parse_contexto(text: str) -> dict[str, str]:
        keys = ("ocupacion", "reto", "intento_fallido")
        empty = {k: "" for k in keys}
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return empty
        try:
            parsed = json.loads(match.group())
            return {k: str(parsed.get(k, "") or "").strip() for k in keys}
        except (json.JSONDecodeError, TypeError):
            return empty

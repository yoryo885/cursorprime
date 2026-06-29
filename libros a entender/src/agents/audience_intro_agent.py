"""Introducción general: para quién está generado el resumen (oficio/audiencia)."""
from __future__ import annotations

from pathlib import Path

from src.output_paths import intro_audiencia_path


class AudienceIntroAgent:
    """Genera un párrafo que explica para qué oficio/audiencia es el resumen."""

    def __init__(self, llm):
        self.llm = llm

    def run(
        self,
        output_dir: Path,
        *,
        libro_nombre: str,
        audiencia: str = "",
        reto: str = "",
        intento_fallido: str = "",
        force: bool = False,
    ) -> str:
        output_dir = Path(output_dir)
        path = intro_audiencia_path(output_dir)

        if path.exists() and not force:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                print(f"   ⏭️  Intro audiencia: reutilizando {path.name}")
                return text

        if not audiencia:
            print("   ⏭️  Intro audiencia: sin oficio/audiencia definido")
            return ""

        if not self.llm:
            return ""

        print(f"   📌 Intro audiencia: para «{audiencia}»...")

        from src.rol_usuario import build_rol_block, ensure_rol_perfil

        profile = ensure_rol_perfil(output_dir, llm=self.llm)
        rol_block = build_rol_block(profile, agent="intro") if profile else ""

        prompt = f"""Eres el redactor que presenta un resumen de libro.

Libro: «{libro_nombre}»
Este resumen está generado PARA: {audiencia}
Reto de esa persona: {reto or "no indicado"}
Lo que intentó sin éxito: {intento_fallido or "no indicado"}

{rol_block}

Escribe UN solo párrafo (3-4 oraciones) que:
- Explique para QUIÉN está hecho este resumen (oficio/audiencia).
- Conecte el libro con su trabajo concreto usando KPIs y léxico del rol.
- Hable de la persona objetivo en «tú» (nunca digas que TÚ eres {audiencia}).
- NO hables de ti como autor del resumen (eso va en otra sección).
- Sin palabras en inglés. Sin tono de autoayuda vacía.

Responde SOLO con el párrafo. Sin título. Sin comillas."""

        text = self.llm.call(prompt).strip().strip('"').strip("«»")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return text

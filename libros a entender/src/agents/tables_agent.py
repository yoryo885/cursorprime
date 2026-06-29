from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from src.agents._paths import tema_slug
from src.agents.book_package import TopicTable
from src.agents.table_subagents import (
    AplicacionVidaRealSubAgent,
    EjemploPracticoSubAgent,
    IdeaClaveSubAgent,
    TableGenerationContext,
    aplicacion_en_primera_persona,
    collect_used_protagonists,
    ejemplo_reuses_protagonist,
    extract_protagonist,
)
from src.output_paths import ensure_book_dirs, tablas_dir
from src.html_renderer import (
    html_to_png,
    render_table_page_html,
    write_html,
)
from src.models import TopicResult
from src.tablas_store import load_tablas_index, save_tablas_index

EMPTY_MARKERS = {"—", "-", "n/a", "na", "none", ""}
ICONOS_VARIANT_INDEX = 2
MAX_CELL_RETRIES = 3


class TablesAgent:
    """Orquesta 3 sub-agentes (idea, ejemplo, aplicación) y renderiza tarjetas."""

    def __init__(self, llm, prompt_extra: Optional[list[str]] = None):
        self.llm = llm
        self.prompt_extra = prompt_extra or []
        self._idea_agent = IdeaClaveSubAgent()
        self._ejemplo_agent = EjemploPracticoSubAgent()
        self._aplicacion_agent = AplicacionVidaRealSubAgent()

    def run(
        self,
        resultados: list[TopicResult],
        libro_nombre: str,
        output_dir: Path,
        *,
        force: bool = False,
        contexto_usuario: dict | None = None,
        only_temas: set[str] | None = None,
    ) -> list[TopicTable]:
        print("   📊 Agente Tablas: 3 sub-agentes + iconos + Playwright...")
        ensure_book_dirs(output_dir)
        tablas_path = tablas_dir(output_dir)
        contexto_usuario = contexto_usuario or self._load_contexto_usuario(output_dir)
        tabla_instrucciones = self._load_tabla_instrucciones(output_dir)
        existing_map = {
            t.tema: t for t in load_tablas_index(tablas_path) if t.tema
        } if only_temas else {}
        tablas = []
        temas_anteriores: list[str] = []
        ejemplos_anteriores: list[str] = []

        for resultado in resultados:
            if resultado.fallo:
                continue

            if only_temas and resultado.tema not in only_temas:
                prev = existing_map.get(resultado.tema)
                if prev:
                    tablas.append(prev)
                    temas_anteriores.append(resultado.tema)
                    ejemplos_anteriores.append(prev.ejemplo_practico)
                    continue

            print(f"      → Tarjeta: '{resultado.tema}' [iconos]...")
            try:
                tabla = self._generar_tabla(
                    resultado,
                    libro_nombre,
                    output_dir=output_dir,
                    temas_anteriores=temas_anteriores,
                    ejemplos_anteriores=ejemplos_anteriores,
                    contexto_usuario=contexto_usuario,
                    tabla_instrucciones=tabla_instrucciones,
                )
                try:
                    tabla.image_path = self._render_html_png(
                        tabla, libro_nombre, tablas_path, force=force
                    )
                except Exception as render_err:
                    print(
                        f"         ⚠️  Render PNG falló en '{resultado.tema}': {render_err}"
                    )
                tablas.append(tabla)
                temas_anteriores.append(resultado.tema)
                ejemplos_anteriores.append(tabla.ejemplo_practico)
            except Exception as err:
                print(f"         ⚠️  Tabla falló en tema '{resultado.tema}': {err}")
                print(
                    f"             temas_anteriores al fallar ({len(temas_anteriores)}): "
                    f"{temas_anteriores}"
                )
                tablas.append(self._tabla_fallback(resultado))
                temas_anteriores.append(resultado.tema)
                ejemplos_anteriores.append(tablas[-1].ejemplo_practico)

        save_tablas_index(tablas_path, tablas)
        return tablas

    def _load_contexto_usuario(self, output_dir: Path) -> dict | None:
        path = Path(output_dir) / "contexto_usuario.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def _render_html_png(
        self,
        tabla: TopicTable,
        libro_nombre: str,
        tablas_dir: Path,
        *,
        force: bool = False,
    ) -> Optional[Path]:
        slug = tema_slug(tabla.tema)
        html_dest = tablas_dir / f"{slug}.html"
        png_dest = tablas_dir / f"{slug}.png"

        if force:
            for path in (html_dest, png_dest):
                if path.exists():
                    path.unlink()
        elif png_dest.exists() and png_dest.stat().st_size > 5000:
            print(f"         ✓ Tabla en caché: {png_dest.name}")
            return png_dest

        content = render_table_page_html(
            tabla, libro_nombre, variant_index=ICONOS_VARIANT_INDEX
        )
        write_html(html_dest, content)
        print(f"         → Playwright render: {png_dest.name}")
        html_to_png(html_dest, png_dest)
        return png_dest

    def _load_tabla_instrucciones(self, output_dir: Path) -> dict[str, str]:
        path = Path(output_dir) / "meta" / "instrucciones_tablas.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {k: str(v) for k, v in data.items() if v}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _build_context(
        self,
        resultado: TopicResult,
        libro_nombre: str,
        output_dir: Path,
        *,
        temas_anteriores: list[str],
        contexto_usuario: dict | None,
        tabla_instrucciones: dict[str, str] | None = None,
    ) -> TableGenerationContext:
        from src.rol_usuario import ensure_rol_perfil

        extra = "\n".join(f"- {i}" for i in self.prompt_extra)
        if tabla_instrucciones:
            guias = "\n".join(
                f"- {k}: {v}" for k, v in tabla_instrucciones.items() if v
            )
            extra += f"\nInstrucciones del planificador:\n{guias}\n"
        extra_block = f"\nInstrucciones extra:\n{extra}\n" if extra else ""
        rol_perfil = ensure_rol_perfil(output_dir, llm=self.llm)
        return TableGenerationContext(
            libro_nombre=libro_nombre,
            tema=resultado.tema,
            texto=resultado.resumen_voz or resultado.resumen,
            extra_block=extra_block,
            temas_anteriores=temas_anteriores,
            contexto_usuario=contexto_usuario,
            rol_perfil=rol_perfil,
        )

    def _generar_tabla(
        self,
        resultado: TopicResult,
        libro_nombre: str,
        output_dir: Path,
        temas_anteriores: Optional[list[str]] = None,
        ejemplos_anteriores: Optional[list[str]] = None,
        contexto_usuario: dict | None = None,
        tabla_instrucciones: dict[str, str] | None = None,
    ) -> TopicTable:
        ctx = self._build_context(
            resultado,
            libro_nombre,
            output_dir,
            temas_anteriores=temas_anteriores or [],
            contexto_usuario=contexto_usuario,
            tabla_instrucciones=tabla_instrucciones,
        )
        ctx.ejemplos_anteriores = ejemplos_anteriores or []
        texto = ctx.texto

        print("         → Sub-agente 1/3: Idea clave")
        ctx.idea_clave = self._generar_celda(
            self._idea_agent,
            ctx,
            resultado.tema,
            texto,
            "idea_clave",
            "idea",
        )

        print("         → Sub-agente 2/3: Ejemplo práctico")
        ejemplo = self._generar_ejemplo(ctx, ejemplos_anteriores or [])

        print("         → Sub-agente 3/3: Aplicación en la vida real")
        ctx.ejemplo_practico = ejemplo
        aplicacion = self._generar_aplicacion(ctx, texto, resultado.tema)

        return TopicTable(
            tema=resultado.tema,
            idea_clave=ctx.idea_clave,
            ejemplo_practico=ejemplo,
            aplicacion_vida_real=aplicacion,
        )

    def _generar_celda(
        self,
        agent,
        ctx: TableGenerationContext,
        tema: str,
        contexto: str,
        field: str,
        tipo: str,
        *,
        extra_retry_hints: list[str] | None = None,
    ) -> str:
        hints = list(extra_retry_hints or [])
        for intento in range(1, MAX_CELL_RETRIES + 1):
            retry_hint = hints[intento - 1] if intento <= len(hints) else ""
            if retry_hint:
                ctx.extra_block = (ctx.extra_block or "") + f"\n{retry_hint}\n"
            raw = self._run_subagent(agent, ctx, retry_hint)
            texto = str(raw or "").strip()
            if texto.lower() not in EMPTY_MARKERS and self._celda_es_valida(texto, field):
                return texto

            print(
                f"         ⚠️  Celda '{tipo}' inválida en '{tema}' "
                f"(intento {intento}/{MAX_CELL_RETRIES}) — reintentando..."
            )
            hints.append(
                f"REINTENTO OBLIGATORIO {intento}: el texto salió truncado o demasiado corto. "
                f"Escribe 2-4 oraciones COMPLETAS con punto final. Campo: {field}."
            )

        print(f"         ⚠️  Celda '{tipo}' sin validar — usando fallback")
        return self._generar_celda_fallback(tema, contexto, tipo)

    def _run_subagent(
        self, agent, ctx: TableGenerationContext, retry_hint: str = ""
    ) -> str:
        if retry_hint and agent in (self._ejemplo_agent, self._aplicacion_agent):
            return agent.run(self.llm, ctx, retry_hint=retry_hint)
        return agent.run(self.llm, ctx)

    @staticmethod
    def _celda_es_valida(texto: str, field: str) -> bool:
        from src.table_validation import celda_es_valida

        return len(texto) >= 10 and celda_es_valida(texto, field)

    def _generar_ejemplo(
        self,
        ctx: TableGenerationContext,
        ejemplos_anteriores: list[str],
    ) -> str:
        from src.table_validation import build_scenario_dedup_hint, ejemplo_reuses_scenario

        ctx.ejemplos_anteriores = ejemplos_anteriores
        retry_hint = ""

        for intento in range(1, MAX_CELL_RETRIES + 1):
            raw = self._run_subagent(self._ejemplo_agent, ctx, retry_hint)
            texto = str(raw or "").strip()
            issues: list[str] = []

            if ejemplo_reuses_protagonist(texto, ejemplos_anteriores):
                issues.append("protagonista repetido")
            prot = extract_protagonist(texto)
            if not prot or prot.lower() == "alguien":
                issues.append("sin protagonista concreto")
            if not self._celda_es_valida(texto, "ejemplo_practico"):
                issues.append("texto truncado o corto")
            if ejemplo_reuses_scenario(texto, ejemplos_anteriores):
                # Aviso blando: guía el reintento pero no bloquea en el último intento
                if intento < MAX_CELL_RETRIES:
                    issues.append("escenario numérico repetido")

            if not issues:
                return texto

            nombres = collect_used_protagonists(ejemplos_anteriores)
            print(
                f"         ⚠️  Ejemplo ({', '.join(issues)}) — "
                f"reintento {intento}/{MAX_CELL_RETRIES}..."
            )
            parts = [
                f"REINTENTO OBLIGATORIO {intento}: corrige {', '.join(issues)}.",
                f"No uses estos nombres: {', '.join(nombres) or 'ninguno'}.",
                "Inventa otra persona, otro oficio y otra escena completamente distintos.",
            ]
            scenario_hint = build_scenario_dedup_hint(ejemplos_anteriores)
            if scenario_hint:
                parts.append(scenario_hint)
            retry_hint = " ".join(parts)
            ctx.extra_block = (ctx.extra_block or "") + f"\n{retry_hint}\n"

        print("         ⚠️  Ejemplo sin validar — usando fallback contextual")
        return self._generar_ejemplo_fallback(ctx)

    def _generar_ejemplo_fallback(self, ctx: TableGenerationContext) -> str:
        return (
            "Cuando revisas tu lista de casos activos, suele ocurrir que un puñado "
            "de estudiantes concentra la mayoría de tus intervenciones urgentes. "
            "Si priorizas ese grupo reducido esta semana, tu gabinete deja de operar "
            "en modo apagar incendios."
        )

    def _generar_aplicacion(
        self,
        ctx: TableGenerationContext,
        texto: str,
        tema: str,
    ) -> str:
        aplicacion = self._generar_celda(
            self._aplicacion_agent,
            ctx,
            tema,
            texto,
            "aplicacion_vida_real",
            "aplicación",
        )
        if not aplicacion_en_primera_persona(aplicacion):
            return aplicacion

        print("         ⚠️  Aplicación en primera persona — reintentando en «tú»...")
        retry_hint = (
            "REINTENTO OBLIGATORIO: la aplicación salió en primera persona "
            "(yo reviso, mi energía, esta semana reviso…). "
            "Reescribe SOLO en segunda persona imperativa: Revisa, Marca, Prioriza, "
            "Identifica, Registra. Prohibido: yo, mi, me, esta semana reviso."
        )
        ctx.extra_block = (ctx.extra_block or "") + f"\n{retry_hint}\n"
        raw = self._run_subagent(self._aplicacion_agent, ctx, retry_hint)
        aplicacion = str(raw or "").strip()
        if self._celda_es_valida(aplicacion, "aplicacion_vida_real"):
            if aplicacion_en_primera_persona(aplicacion):
                print("         ⚠️  Sigue en primera persona; corrigiendo imperativos básicos")
                aplicacion = self._forzar_aplicacion_tu(aplicacion)
            return aplicacion

        return self._generar_celda(
            self._aplicacion_agent,
            ctx,
            tema,
            texto,
            "aplicacion_vida_real",
            "aplicación",
            extra_retry_hints=[retry_hint],
        )

    @staticmethod
    def _forzar_aplicacion_tu(texto: str) -> str:
        """Conversión mínima de patrones frecuentes en primera persona."""
        t = texto
        reemplazos = (
            (r"(?i)^esta semana reviso", "Revisa"),
            (r"(?i)^esta semana marco", "Marca"),
            (r"(?i)^esta semana identifico", "Identifica"),
            (r"(?i)\byo reviso\b", "revisa"),
            (r"(?i)\byo priorizo\b", "prioriza"),
            (r"(?i)\bdejo de\b", "Deja de"),
            (r"(?i)\bme concentro\b", "concéntrate"),
            (r"(?i)\binvierto mi energía\b", "invierte tu energía"),
            (r"(?i)\bmi lista\b", "tu lista"),
            (r"(?i)\bmi agenda\b", "tu agenda"),
            (r"(?i)\bmi energía\b", "tu energía"),
        )
        for patron, repl in reemplazos:
            t = re.sub(patron, repl, t)
        return t.strip()

    def _celda(self, valor, tema: str, contexto: str, tipo: str) -> str:
        texto = str(valor or "").strip()
        if texto.lower() not in EMPTY_MARKERS and len(texto) >= 10:
            return texto
        print(f"         ⚠️  Celda '{tipo}' vacía o inválida en tema '{tema}' — usando fallback")
        return self._generar_celda_fallback(tema, contexto, tipo)

    def _generar_celda_fallback(self, tema: str, contexto: str, tipo: str) -> str:
        extracto = contexto[:150].strip() if contexto else tema
        fallbacks = {
            "idea": (
                f"Algo que aprendí sobre «{tema}»: {extracto[:120]}. "
                f"No lo tenía claro antes. Ahora sí."
            ),
            "ejemplo": (
                f"Alguien aplica «{tema}» y descubre que estaba invirtiendo "
                f"su energía en lo que menos importaba. "
                f"Cambia el foco. Los resultados cambian solos."
            ),
            "aplicación": (
                "Esta semana elige una sola acción concreta. "
                "Marca qué cosas dejas de hacer y cuál es tu único foco. "
                "Sin dispersarte."
            ),
        }
        return fallbacks.get(tipo, extracto)

    def _tabla_fallback(self, resultado: TopicResult) -> TopicTable:
        return self._tabla_fallback_from_context(
            resultado.tema, resultado.resumen_voz or resultado.resumen
        )

    def _tabla_fallback_from_context(self, tema: str, contexto: str) -> TopicTable:
        return TopicTable(
            tema=tema,
            idea_clave=self._generar_celda_fallback(tema, contexto, "idea"),
            ejemplo_practico=self._generar_celda_fallback(tema, contexto, "ejemplo"),
            aplicacion_vida_real=self._generar_celda_fallback(tema, contexto, "aplicación"),
        )

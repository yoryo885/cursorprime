"""
cost_estimator.py — estima costo y tiempo antes de gastar tokens reales.

Incluye resúmenes, corrección, tablas (3 sub-agentes × tema), mapa, intros y QC.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.config import CLAUDE_MODEL

PRECIO_POR_MILLON: dict[str, float] = {
    "input": 3.0,
    "output": 15.0,
}

CHARS_POR_TOKEN = 4
CHUNKS_POR_TEMA = 5
CHARS_POR_CHUNK = 1500


@dataclass(frozen=True)
class _Fase:
    nombre: str
    llamadas: float
    tokens_entrada: int
    tokens_salida: int
    minutos: float


def _costo_usd(tokens_in: int, tokens_out: int) -> float:
    return (
        tokens_in * PRECIO_POR_MILLON["input"]
        + tokens_out * PRECIO_POR_MILLON["output"]
    ) / 1_000_000


def _chunk_tokens() -> int:
    return int(CHUNKS_POR_TEMA * CHARS_POR_CHUNK / CHARS_POR_TOKEN)


def _fase_resumenes(n: int) -> _Fase:
    """Subagent + corrector + ~15 % reintentos por calidad."""
    chunk_tok = _chunk_tokens()
    por_llamada_in = 550 + chunk_tok
    por_llamada_out = 520
    llamadas = n * 2.15  # analyze + corrector + reintentos
    return _Fase(
        "Resúmenes por tema",
        llamadas,
        int(por_llamada_in * llamadas),
        int(por_llamada_out * llamadas),
        round(n * 1.6, 1),
    )


def _fase_tablas(n: int, *, factor_reintentos: float = 1.22) -> _Fase:
    """3 sub-agentes por tema (idea, ejemplo, aplicación) + reintentos de validación."""
    por_celda_in = 1550  # prompt + resumen del tema + dedup creciente
    por_celda_out = 190
    llamadas = n * 3 * factor_reintentos
    return _Fase(
        "Tablas editoriales (3× tema)",
        llamadas,
        int(por_celda_in * llamadas),
        int(por_celda_out * llamadas),
        round(n * 1.1, 1),
    )


def _fase_mapa() -> _Fase:
    return _Fase("Mapa conceptual", 1.0, 2800, 650, 0.8)


def _fase_intro_yordy() -> _Fase:
    return _Fase("Intro Yordy", 1.0, 950, 380, 0.4)


def _fase_intro_audiencia() -> _Fase:
    return _Fase("Intro audiencia", 1.0, 720, 220, 0.3)


def _fase_qc(n: int) -> _Fase:
    return _Fase(
        "QC final (LLM)",
        1.0,
        2600 + n * 380,
        480,
        0.4,
    )


def _fase_qc_autofix(n: int) -> _Fase:
    """Hasta 2 rondas de regeneración parcial (~15 % tablas extra)."""
    extra = _fase_tablas(n, factor_reintentos=0.15)
    return _Fase(
        "QC auto-fix (reserva)",
        extra.llamadas,
        extra.tokens_entrada,
        extra.tokens_salida,
        round(extra.minutos * 0.5, 1),
    )


def _fase_planificador() -> _Fase:
    return _Fase("Planificador", 1.0, 2100, 750, 0.5)


MODOS = frozenset({
    "completo",
    "resumenes",
    "tablas",
    "enriquecer",
    "mapa",
    "intros",
    "pdf",
    "planificar",
})


def estimar(
    pdf_text: str,
    temas: list[str],
    *,
    modo: str = "completo",
    sin_qc: bool = False,
    incluir_autofix: bool = True,
) -> dict:
    """
    Estima tokens, costo y tiempo según el modo de ejecución.

    Modos: completo | resumenes | tablas | enriquecer | mapa | intros | pdf | planificar
    """
    _ = pdf_text  # reservado: ajuste futuro por tamaño del PDF
    modo = modo if modo in MODOS else "completo"
    n = max(len(temas), 1)
    fases: list[_Fase] = []

    if modo in ("completo", "resumenes", "planificar"):
        fases.append(_fase_resumenes(n))

    if modo in ("completo", "tablas", "enriquecer", "planificar"):
        fases.append(_fase_tablas(n))

    if modo in ("completo", "enriquecer", "planificar"):
        fases.append(_fase_mapa())
        fases.append(_fase_intro_yordy())
        fases.append(_fase_intro_audiencia())

    if modo == "mapa":
        fases.append(_fase_mapa())

    if modo == "intros":
        fases.append(_fase_intro_audiencia())

    if modo == "planificar":
        fases.append(_fase_planificador())

    if modo in ("completo", "enriquecer", "pdf", "planificar") and not sin_qc:
        fases.append(_fase_qc(n))
        if incluir_autofix and modo in ("completo", "enriquecer", "planificar"):
            fases.append(_fase_qc_autofix(n))

    tokens_in = sum(f.tokens_entrada for f in fases)
    tokens_out = sum(f.tokens_salida for f in fases)
    llamadas = round(sum(f.llamadas for f in fases), 1)
    minutos = round(sum(f.minutos for f in fases), 1)

    desglose = [
        {
            "fase": f.nombre,
            "llamadas": round(f.llamadas, 1),
            "tokens_entrada": f.tokens_entrada,
            "tokens_salida": f.tokens_salida,
            "minutos": f.minutos,
        }
        for f in fases
    ]

    return {
        "modelo": CLAUDE_MODEL,
        "modo": modo,
        "temas": n,
        "llamadas_estimadas": llamadas,
        "tokens_entrada_estimados": tokens_in,
        "tokens_salida_estimados": tokens_out,
        "tokens_totales": tokens_in + tokens_out,
        "costo_usd": round(_costo_usd(tokens_in, tokens_out), 4),
        "tiempo_estimado_min": minutos,
        "desglose": desglose,
    }


def modo_desde_main(args) -> str:
    """Infere el modo de coste a partir de flags de main.py."""
    if getattr(args, "solo_resumenes", False):
        return "resumenes"
    if getattr(args, "solo_tablas", False):
        return "tablas"
    if getattr(args, "solo_mapa", False):
        return "mapa"
    if getattr(args, "solo_intros", False):
        return "intros"
    if getattr(args, "solo_pdf", False):
        return "pdf"
    if getattr(args, "solo_enriquecer", False):
        return "enriquecer"
    return "completo"


def mostrar_y_confirmar(estimacion: dict) -> bool:
    print("\n📊 Estimación de costo:")
    print(f"   Modelo:         {estimacion['modelo']}")
    print(f"   Modo:           {estimacion.get('modo', 'completo')}")
    print(f"   Temas:          {estimacion['temas']}")
    print(f"   Llamadas LLM:   ~{estimacion.get('llamadas_estimadas', '?')}")
    print(f"   Tokens totales: ~{estimacion['tokens_totales']:,}")
    print(f"   Costo aprox:    ${estimacion['costo_usd']} USD")
    print(f"   Tiempo aprox:   {estimacion['tiempo_estimado_min']} min")

    desglose = estimacion.get("desglose") or []
    if desglose:
        print("   Desglose:")
        for item in desglose:
            print(
                f"      · {item['fase']}: ~{item['llamadas']} llamadas, "
                f"~{item['minutos']} min"
            )
    print()
    respuesta = input("¿Continuar? (s/n): ").strip().lower()
    return respuesta == "s"

"""Validación de calidad del listing KDP y detección de problemas del PDF (solo lectura)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.marketing.context_loader import MarketingContext
from src.marketing.models import KDPListing
from src.marketing.pdf_reader import extract_pdf_content
from src.marketing.utils import KDP_PROHIBIDAS, load_contexto_cercano
from src.serie import load_serie_config

if TYPE_CHECKING:
    pass


@dataclass
class PDFContentIssue:
    """Problema del PDF de producción — marketing NO lo corrige."""

    tipo: str
    problema: str
    solicitud: str
    prioridad: str = "media"
    contexto: dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketingQCReport:
    score: float = 0.0
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passed: bool = False

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": self.passed,
        }


def _strip_html(texto: str) -> str:
    return re.sub(r"<[^>]+>", " ", texto or "")


def _contiene_prohibidas(texto: str) -> list[str]:
    found = []
    lower = (texto or "").lower()
    for p in KDP_PROHIBIDAS:
        if p in lower:
            found.append(p)
    return found


def validate_listing(
    listing: KDPListing,
    marketing_ctx: MarketingContext | None = None,
) -> MarketingQCReport:
    issues: list[str] = []
    warnings: list[str] = []
    puntos = 0.0
    max_puntos = 10.0

    titulo = (listing.titulo or "").strip()
    if not titulo:
        issues.append("titulo_vacio")
    elif len(titulo) < 20:
        issues.append("titulo_muy_corto")
        warnings.append(f"Título corto ({len(titulo)} chars); ideal 40-120")
    elif len(titulo) > 200:
        issues.append("titulo_excede_200")
    else:
        puntos += 2.0
        if 40 <= len(titulo) <= 120:
            puntos += 0.5

    prohibidas_t = _contiene_prohibidas(titulo)
    if prohibidas_t:
        issues.append("titulo_palabras_prohibidas")
        warnings.append(f"Prohibidas en título: {', '.join(prohibidas_t)}")

    desc_plain = _strip_html(listing.descripcion_html)
    palabras = len(desc_plain.split())
    if palabras < 280:
        issues.append("descripcion_muy_corta")
        warnings.append(f"Descripción ~{palabras} palabras; KDP ideal 300-400")
    elif palabras > 450:
        warnings.append(f"Descripción larga (~{palabras} palabras)")
        puntos += 1.5
    else:
        puntos += 2.0

    prohibidas_d = _contiene_prohibidas(desc_plain)
    if prohibidas_d:
        issues.append("descripcion_palabras_prohibidas")

    if listing.disclaimer and listing.disclaimer.lower() not in desc_plain.lower():
        warnings.append("disclaimer_no_aparece_en_descripcion")
    else:
        puntos += 1.0

    kws = [k for k in listing.keywords if k.strip()]
    if len(kws) < 7:
        issues.append("keywords_insuficientes")
    else:
        puntos += 2.0
    for kw in kws:
        if len(kw) > 50:
            warnings.append(f"Keyword larga: {kw[:30]}...")

    beneficios = [b for b in listing.beneficios if b.strip()]
    if len(beneficios) < 5:
        issues.append("beneficios_insuficientes")
    else:
        puntos += 1.5

    audiencia = (listing.analisis.audiencia or "").strip()
    audiencia_meta = ""
    if marketing_ctx:
        audiencia_meta = marketing_ctx.audiencia.strip()
    if audiencia or audiencia_meta:
        ok_audiencia = _audiencia_presente(audiencia, desc_plain) if audiencia else False
        if not ok_audiencia and audiencia_meta:
            ok_audiencia = _audiencia_presente(audiencia_meta, desc_plain)
        if not ok_audiencia:
            warnings.append("audiencia_no_mencionada_en_descripcion")
        else:
            puntos += 1.0
    else:
        puntos += 1.0

    if listing.serie and listing.serie.lower() not in desc_plain.lower():
        warnings.append("serie_no_mencionada_en_descripcion")

    if marketing_ctx and marketing_ctx.portada_aprobada and marketing_ctx.titulo_pdf:
        if not _titulo_comercial_presente(marketing_ctx.titulo_pdf, titulo):
            issues.append("titulo_no_alineado_con_portada_pdf")
            warnings.append(
                f"El título KDP debe reflejar la portada aprobada: «{marketing_ctx.titulo_pdf}»"
            )
        else:
            puntos += 0.5
        if "10 semana" in marketing_ctx.titulo_pdf.lower() and "10 semana" not in titulo.lower():
            warnings.append("titulo_sin_promesa_10_semanas_de_portada")
        if marketing_ctx.semanas_plan and str(marketing_ctx.semanas_plan) not in desc_plain:
            warnings.append("descripcion_sin_mencionar_plan_semanas")

    if marketing_ctx and marketing_ctx.lexico_rol:
        desc_kw_text = f"{desc_plain} {' '.join(listing.keywords)}".lower()
        if not any(term.lower() in desc_kw_text for term in marketing_ctx.lexico_rol[:5]):
            warnings.append("lexico_rol_ausente_en_listing")

    if listing.subtitulo and len(listing.subtitulo) > 200:
        warnings.append("subtitulo_excede_200")

    if marketing_ctx and marketing_ctx.kdp_seed.get("titulo_kdp"):
        seed = str(marketing_ctx.kdp_seed["titulo_kdp"])
        if seed.strip().lower() != titulo.strip().lower() and not _titulo_comercial_presente(
            seed, titulo
        ):
            warnings.append("titulo_difiere_del_borrador_kdp_listing")

    score = round(min(10.0, (puntos / max_puntos) * 10), 1)
    passed = len(issues) == 0 and score >= 6.0

    return MarketingQCReport(
        score=score,
        issues=issues,
        warnings=warnings,
        passed=passed,
    )


def _titulo_comercial_presente(esperado: str, texto: str) -> bool:
    esperado = (esperado or "").strip().lower()
    if not esperado:
        return True
    if esperado in texto.lower():
        return True
    palabras = [w for w in esperado.split() if len(w) > 3]
    if not palabras:
        return True
    hits = sum(1 for p in palabras if p in texto.lower())
    return hits / len(palabras) >= 0.85


def _normalizar_palabra_rol(palabra: str) -> str:
    w = palabra.lower()
    for suf in ("aciones", "ación", "mente", "as", "os", "es", "a", "o"):
        if len(w) > len(suf) + 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _audiencia_presente(audiencia: str, texto: str) -> bool:
    """True si la descripción refleja la audiencia (exacta o por términos clave del rol)."""
    audiencia = (audiencia or "").strip().lower()
    texto = (texto or "").lower()
    if not audiencia:
        return True
    if audiencia in texto:
        return True
    palabras = [w for w in re.findall(r"\w+", audiencia) if len(w) > 3]
    if palabras:
        hits = sum(1 for p in palabras if p in texto)
        if hits / len(palabras) >= 0.6:
            return True
        raices = [_normalizar_palabra_rol(p) for p in palabras]
        hits_raiz = sum(1 for r in raices if len(r) >= 5 and r in texto)
        if hits_raiz / len(palabras) >= 0.5:
            return True
    rol = audiencia.split()[0] if audiencia.split() else ""
    if len(rol) >= 8:
        raiz = _normalizar_palabra_rol(rol)
        if raiz in texto:
            return True
    return False


def detect_pdf_content_issues(
    pdf_path: Path,
    *,
    listing: KDPListing | None = None,
) -> list[PDFContentIssue]:
    """
    Lee el PDF (solo lectura) y detecta desalineaciones con la marca/rol.
    Cualquier issue aquí se escala a producción — marketing nunca edita el PDF.
    """
    path = Path(pdf_path)
    issues: list[PDFContentIssue] = []
    pdf = extract_pdf_content(path)
    texto = pdf.texto_completo.lower()
    primera_pagina = (pdf.texto_completo.split("\n\n")[0] if pdf.texto_completo else "").lower()

    cfg = load_serie_config()
    serie_esperada = str(cfg.get("nombre_serie") or "Aplicar en tu rol").lower()
    ctx = load_contexto_cercano(path)
    producto = ctx.get("producto") if isinstance(ctx.get("producto"), dict) else {}

    titulo_comercial = str(producto.get("titulo_comercial") or "").strip()
    serie_producto = str(producto.get("serie_nombre") or serie_esperada).strip()
    portada_aprobada = bool(producto.get("portada_aprobada"))

    if (
        not portada_aprobada
        and serie_esperada
        and serie_esperada not in primera_pagina
        and "resumen personal" in primera_pagina
    ):
            issues.append(
                PDFContentIssue(
                    tipo="portada",
                    prioridad="alta",
                    problema="La portada del PDF aún dice «Resumen personal» en lugar de la serie.",
                    solicitud=(
                        f"Regenerar portada con label «{serie_producto}» y título comercial "
                        f"«{titulo_comercial or 'según producto.json'}». "
                        "Ejecutar: python main.py --solo-pdf --slug {slug}"
                    ).format(slug=path.parent.name),
                    contexto={"esperado": serie_producto, "encontrado": "Resumen personal"},
                )
            )

    if (
        titulo_comercial
        and not portada_aprobada
        and not _titulo_comercial_presente(titulo_comercial, pdf.texto_completo)
    ):
        issues.append(
            PDFContentIssue(
                tipo="portada",
                prioridad="alta",
                problema=f"El título comercial «{titulo_comercial}» no aparece en el PDF.",
                solicitud=(
                    "Actualizar producto.json si cambió la serie y regenerar PDF con "
                    "python main.py --solo-pdf --slug " + path.parent.name
                ),
                contexto={"titulo_esperado": titulo_comercial},
            )
        )

    audiencia_ctx = str(ctx.get("audiencia") or "").strip()
    audiencia_listing = (listing.analisis.audiencia if listing else "") or audiencia_ctx
    if audiencia_ctx and audiencia_ctx.lower() not in texto:
        issues.append(
            PDFContentIssue(
                tipo="audiencia",
                prioridad="media",
                problema=f"La audiencia «{audiencia_ctx}» no está reflejada claramente en el PDF.",
                solicitud=(
                    "Regenerar intro de audiencia y páginas de rol con AudienceIntroAgent. "
                    f"python main.py --solo-intros --slug {path.parent.name}"
                ),
                contexto={"audiencia": audiencia_ctx},
            )
        )

    if pdf.num_paginas < 5:
        issues.append(
            PDFContentIssue(
                tipo="contenido",
                prioridad="alta",
                problema=f"El PDF tiene solo {pdf.num_paginas} página(s); parece incompleto para vender.",
                solicitud=(
                    "Ejecutar pipeline de producción completa o --solo-enriquecer "
                    f"para slug {path.parent.name}"
                ),
                contexto={"paginas": pdf.num_paginas},
            )
        )

    if "plan de acción" not in texto and "plan de accion" not in texto:
        issues.append(
            PDFContentIssue(
                tipo="plan_accion",
                prioridad="media",
                problema="No se detectó plan de acción en el PDF.",
                solicitud=(
                    f"Regenerar plan de acción: python main.py --solo-plan-accion --slug {path.parent.name}"
                ),
            )
        )

    return issues

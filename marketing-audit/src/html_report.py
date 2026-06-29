"""Genera informe HTML en español — formato vendible al cliente."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from src.client_language import PRIORIDAD_PESO, SEVERIDAD_CLIENTE, resumen_ejecutivo

CATEGORIAS_ES = {
    "Content & Messaging": "Contenido y mensaje",
    "Conversion Optimization": "Conversión (ventas)",
    "SEO & Discoverability": "Google y visibilidad",
    "Competitive Positioning": "Competencia",
    "Brand & Trust": "Marca y confianza",
    "Growth & Strategy": "Crecimiento",
}

SEVERIDAD_CSS = {
    "critical": ("Urgente", "critical"),
    "high": ("Importante", "high"),
    "medium": ("A mejorar", "medium"),
    "low": ("Opcional", "medium"),
}

GRADO_ES = {"A": "Excelente", "B": "Bueno", "C": "Regular", "D": "Bajo", "F": "Crítico"}


def _grado_texto(score: int, grade: str) -> str:
    g = GRADO_ES.get(grade, grade)
    if score < 60:
        return f"Tu web pierde clientes en Google y en la primera visita. Hay mejoras urgentes. (Nota {g})"
    if score < 75:
        return f"Base aceptable, pero compites por debajo de negocios similares. (Nota {g})"
    return f"Buen nivel; optimizaciones puntuales pueden sumar más consultas. (Nota {g})"


def _wa_link(numero: str, mensaje: str) -> str:
    n = "".join(c for c in numero if c.isdigit())
    return f"https://wa.me/{n}?text={quote(mensaje)}"


def generar_html(syn: dict, out_path: Path, branding: dict | None = None) -> Path:
    brand = syn.get("brand_name", "Negocio")
    score = syn.get("overall_score", 0)
    grade = syn.get("grade", "C")
    url = syn.get("url", "")

    filas = ""
    for cat, data in (syn.get("categories") or {}).items():
        nombre = CATEGORIAS_ES.get(cat, cat)
        prio = PRIORIDAD_PESO.get(str(data.get("weight")), data.get("weight"))
        filas += f"<tr><td>{nombre}</td><td><strong>{data.get('score')}</strong>/100</td><td>{prio}</td></tr>\n"

    hallazgos = ""
    for f in syn.get("findings") or []:
        sev, css = SEVERIDAD_CSS.get(f.get("severity", "medium"), ("A mejorar", "medium"))
        titulo = f.get("client_title") or f.get("title")
        detalle = f.get("client_detail") or f.get("detail")
        accion = f.get("client_action") or ""
        hallazgos += (
            f'<div class="finding {css}"><span class="tag">{sev}</span> '
            f"<strong>{titulo}</strong><br>{detalle}"
        )
        if accion:
            hallazgos += f'<br><em>Qué hacer:</em> {accion}'
        hallazgos += "</div>\n"

    wins = ""
    for i, w in enumerate(syn.get("quick_wins") or [], 1):
        wins += f"<li>{w}</li>\n"

    competidores = ""
    for c in (syn.get("competitors") or [])[:5]:
        tier = {"direct": "competidor directo", "aspirational": "referente del rubro", "indirect": "alternativa"}.get(
            c.get("tier", ""), ""
        )
        extra = f" — {tier}" if tier else ""
        competidores += f"<li><strong>{c.get('name')}</strong>{extra}</li>\n"

    resumen = resumen_ejecutivo(score, grade, brand).replace("**", "")

    demo = syn.get("mock", False)
    badge = '<span class="badge">Informe de demostración</span>' if demo else ""

    b = branding or {}
    consultor = b.get("nombre", "Consultor")
    wa_num = b.get("whatsapp", "")
    wa_msg = b.get("whatsapp_mensaje", "Hola, quiero agendar la llamada sobre el informe de marketing.")
    email = b.get("email", "")
    wa_url = _wa_link(wa_num, wa_msg) if wa_num else "#"

    logo_block = '<div class="logo-text">' + consultor + "</div>"
    logo_file = out_path.parent / "logo.svg"
    if logo_file.exists():
        logo_block = f'<img src="logo.svg" alt="{consultor}" class="logo" />'

    contacto_extra = f' · <a href="mailto:{email}">{email}</a>' if email else ""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Informe de marketing — {brand}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: Georgia, 'Times New Roman', serif; max-width: 680px; margin: 0 auto; padding: 2rem 1.25rem; color: #1c1917; line-height: 1.6; background: #fff; }}
    .header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; border-bottom: 3px solid #0f766e; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
    .logo {{ height: 44px; width: auto; }}
    .logo-text {{ font-family: system-ui, sans-serif; font-weight: 700; color: #0f766e; font-size: 1rem; }}
    .header-right {{ text-align: right; font-family: system-ui, sans-serif; font-size: 0.8rem; color: #57534e; }}
    .header-right a {{ color: #0f766e; text-decoration: none; font-weight: 600; }}
    h1 {{ font-size: 1.4rem; margin: 1rem 0 0.25rem; color: #0f766e; clear: both; }}
    .sub {{ font-family: system-ui, sans-serif; color: #57534e; font-size: 0.9rem; }}
    .score-box {{ background: linear-gradient(135deg, #f0fdfa 0%, #ecfdf5 100%); border: 1px solid #99f6e4; border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1.5rem 0; }}
    .score {{ font-family: system-ui, sans-serif; font-size: 3.5rem; font-weight: 800; color: #0f766e; line-height: 1; }}
    .score-label {{ font-family: system-ui, sans-serif; font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }}
    .resumen {{ background: #fafaf9; padding: 1rem 1.25rem; border-radius: 8px; margin: 1.5rem 0; font-size: 1.05rem; }}
    h2 {{ font-family: system-ui, sans-serif; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.06em; color: #0f766e; margin-top: 2rem; }}
    table {{ width: 100%; border-collapse: collapse; font-family: system-ui, sans-serif; font-size: 0.88rem; }}
    th, td {{ padding: 0.6rem 0.5rem; border-bottom: 1px solid #e7e5e4; text-align: left; }}
    th {{ color: #78716c; font-weight: 600; }}
    .finding {{ font-family: system-ui, sans-serif; padding: 0.85rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; border-left: 4px solid #a8a29e; background: #fafaf9; font-size: 0.92rem; }}
    .critical {{ border-color: #dc2626; background: #fef2f2; }}
    .high {{ border-color: #ea580c; background: #fff7ed; }}
    .medium {{ border-color: #ca8a04; background: #fefce8; }}
    .tag {{ font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: #57534e; display: block; margin-bottom: 0.25rem; }}
    .cta {{ background: #0f766e; color: #fff; font-family: system-ui, sans-serif; padding: 1.25rem 1.5rem; border-radius: 12px; margin-top: 2rem; text-align: center; }}
    .cta a {{ display: inline-block; margin-top: 0.75rem; background: #fff; color: #0f766e; padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 0.95rem; }}
    .badge {{ display: inline-block; background: #fef3c7; color: #92400e; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-family: system-ui, sans-serif; }}
    footer {{ margin-top: 2rem; font-family: system-ui, sans-serif; font-size: 0.75rem; color: #a8a29e; text-align: center; }}
    ul {{ padding-left: 1.2rem; }}
  </style>
</head>
<body>
  <div class="header">
    {logo_block}
    <div class="header-right">
      <strong>{consultor}</strong><br>
      <a href="{wa_url}" target="_blank">WhatsApp</a>{contacto_extra}
    </div>
  </div>
  <h1>Informe de marketing digital</h1>
  <p class="sub"><strong>{brand}</strong><br>{url} · {badge}</p>

  <div class="score-box">
    <div class="score">{score}<span style="font-size:1.2rem;color:#64748b">/100</span></div>
    <div class="score-label">Puntuación de marketing online</div>
  </div>

  <div class="resumen">
    {resumen}
  </div>

  <h2>Cómo va cada área</h2>
  <table>
    <thead><tr><th>Área</th><th>Nota</th><th>Prioridad</th></tr></thead>
    <tbody>{filas}</tbody>
  </table>

  <h2>Qué encontramos</h2>
  {hallazgos or '<p>Sin hallazgos críticos registrados.</p>'}

  <h2>Arreglos rápidos (esta semana)</h2>
  <ul>{wins or '<li>Revisar textos de la página principal</li>'}</ul>

  <h2>Competencia en tu zona</h2>
  <ul>{competidores or '<li>Pendiente análisis con web real</li>'}</ul>

  <div class="cta">
    <strong>¿Quieres que lo arreglemos por ti?</strong>
    <p>Agenda una llamada de 20 min — te mostramos el plan sin compromiso.</p>
    <a href="{wa_url}" target="_blank">Escríbenos por WhatsApp</a>
  </div>

  <footer>Informe preparado por {consultor} · Confidencial · {syn.get('synthesized_at', '')[:10]}</footer>
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")
    return out_path

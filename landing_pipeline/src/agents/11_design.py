"""11 — Design: copy.json + design_skill → landing.html (sin overlap, un acento)."""

from __future__ import annotations

import html
from typing import Any

from src.agents.base import load_skill
from src.llm_client import LLMClient
from src.text_utils import public_name


def _e(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def _build_html(brief: dict, copy: dict) -> str:
    nombre = public_name(brief)
    hero = copy.get("hero") or {}
    social = copy.get("social_proof") or {}
    problem = copy.get("problem") or {}
    benefits = copy.get("benefits") or {}
    testimonials = copy.get("testimonials") or {}
    pricing = copy.get("pricing") or {}
    faq = copy.get("faq") or {}
    cta = copy.get("cta_final") or {}
    footer = copy.get("footer") or {}

    dolores = "".join(f"<li>{_e(d)}</li>" for d in (problem.get("dolores") or [])[:3])
    bens = "".join(
        f'<article class="ben"><h3>{_e(i.get("titulo"))}</h3><p>{_e(i.get("texto"))}</p></article>'
        for i in (benefits.get("items") or [])[:5]
    )

    omitida = bool(testimonials.get("omitida"))
    tests = testimonials.get("items") or []
    test_html = ""
    if not omitida and tests:
        test_html = (
            '<section id="testimonios" class="flow"><h2>Lo que dicen</h2><div class="tests">'
            + "".join(
                f'<blockquote><p>“{_e(t.get("quote"))}”</p>'
                f'<cite>{_e(t.get("nombre"))} · {_e(t.get("cargo"))}</cite></blockquote>'
                for t in tests[:3]
            )
            + "</div></section>"
        )

    incluye = "".join(f"<li>{_e(x)}</li>" for x in (pricing.get("incluye") or [])[:3])
    faqs = "".join(
        f"<details><summary>{_e(f.get('q'))}</summary><p>{_e(f.get('a'))}</p></details>"
        for f in (faq.get("items") or [])[:6]
    )
    legales = " · ".join(
        f'<a href="#">{_e(x)}</a>' for x in (footer.get("legales") or ["Privacidad", "Términos"])
    )
    redes = footer.get("redes") or []
    redes_html = " · ".join(_e(r) for r in redes) if redes else ""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(nombre)} — {_e(hero.get('titulo') or brief.get('propuesta_valor') or '')}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Outfit:wght@400;500;600&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --ink:#1b222c;
      --paper:#f4f1ec;
      --accent:#c9a962;
      --muted:#7a847c;
      --sand:#ebe6df;
      --pad:clamp(16px,4vw,40px);
      --max:960px;
    }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{
      font-family:Outfit,system-ui,sans-serif;
      background:var(--paper);
      color:var(--ink);
      line-height:1.55;
    }}
    /* Header: único sticky permitido */
    .top {{
      display:flex; justify-content:space-between; align-items:center;
      padding:14px var(--pad); border-bottom:1px solid #e4dfd6;
      position:sticky; top:0; z-index:10;
      background:var(--paper);
    }}
    .logo {{
      font-family:"Cormorant Garamond",Georgia,serif; letter-spacing:.16em;
      font-weight:600; font-size:1.35rem; text-decoration:none; color:var(--ink);
    }}
    .nav a {{
      color:var(--muted); text-decoration:none; font-size:.72rem;
      letter-spacing:.08em; text-transform:uppercase; margin-left:14px;
    }}
    /* Secciones: flujo normal, sin absolute/fixed de contenido, sin overlap */
    section.flow, .proof, .cta-final, footer {{
      position:relative;
      display:block;
      width:100%;
      clear:both;
      isolation:isolate;
      overflow:hidden;
    }}
    section.flow {{
      padding:clamp(48px,8vw,72px) var(--pad);
      background:var(--paper);
    }}
    section.flow.band {{ background:var(--sand); }}
    section.flow > .inner, .cta-final > .inner {{
      max-width:var(--max); margin:0 auto;
    }}
    .hero.flow {{
      min-height:min(70svh,600px);
      padding:clamp(48px,10vh,88px) var(--pad);
      background:linear-gradient(125deg, #1b222c 0%, #2a3544 55%, #3a4555 100%);
      color:#f0ebe3;
      display:flex; align-items:flex-end;
    }}
    .brand-hero {{
      font-family:"Cormorant Garamond",Georgia,serif; letter-spacing:.18em; font-weight:600;
      font-size:clamp(2rem,5vw,3.2rem); margin-bottom:12px;
    }}
    .hero h1 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:clamp(1.4rem,3vw,1.85rem); max-width:18ch; line-height:1.2; margin-bottom:12px;
    }}
    .hero .sub {{ color:rgba(240,235,227,.8); max-width:40ch; margin-bottom:22px; }}
    /* UN solo acento para TODOS los botones primarios */
    .btn {{
      display:inline-flex; align-items:center; justify-content:center;
      min-height:50px; padding:0 26px;
      background:var(--accent); color:var(--ink);
      font-size:.72rem; font-weight:600; letter-spacing:.12em;
      text-transform:uppercase; text-decoration:none; border:none; cursor:pointer;
    }}
    .proof {{
      text-align:center; padding:18px var(--pad);
      border-bottom:1px solid #e4dfd6; background:var(--paper);
      font-size:.9rem; color:var(--muted);
    }}
    .proof strong {{ color:var(--ink); font-weight:600; }}
    h2 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:clamp(1.4rem,3vw,1.9rem); text-align:center; margin-bottom:14px;
    }}
    .dolores {{ list-style:none; padding:0; max-width:40ch; margin:0 auto; }}
    .dolores li {{ padding:12px 0; border-bottom:1px solid #e4dfd6; color:var(--muted); }}
    .puente {{ text-align:center; margin-top:22px; font-weight:500; }}
    .bens {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; }}
    .ben {{ background:#fff; border:1px solid #e4dfd6; padding:20px; }}
    .ben h3 {{ font-family:"Cormorant Garamond",Georgia,serif; font-weight:500; margin-bottom:8px; }}
    .ben p {{ color:var(--muted); font-size:.92rem; }}
    .tests {{ display:grid; gap:14px; max-width:52ch; margin:0 auto; }}
    blockquote {{ background:#fff; border:1px solid #e4dfd6; padding:18px; }}
    blockquote p {{ font-size:1.02rem; margin-bottom:10px; }}
    cite {{ font-style:normal; font-size:.8rem; color:var(--muted); }}
    .price-box {{ text-align:center; max-width:28rem; margin:0 auto; }}
    .price {{ font-size:clamp(1.6rem,4vw,2.2rem); font-weight:600; margin:8px 0 16px; }}
    .incluye {{ list-style:none; padding:0; text-align:left; margin:0 auto 22px; max-width:28ch; }}
    .incluye li {{ padding:10px 0; border-bottom:1px solid #e4dfd6; color:var(--muted); }}
    details {{ background:#fff; border:1px solid #e4dfd6; padding:14px 16px; margin-bottom:10px; }}
    summary {{ cursor:pointer; font-weight:500; }}
    details p {{ margin-top:8px; color:var(--muted); font-size:.92rem; }}
    .cta-final {{
      text-align:center; padding:clamp(48px,8vw,72px) var(--pad);
      background:#1b222c; color:#f0ebe3;
    }}
    .cta-final h2 {{ color:#f0ebe3; }}
    .cta-final p {{ color:rgba(240,235,227,.75); max-width:40ch; margin:0 auto 20px; }}
    footer {{
      text-align:center; padding:28px var(--pad); font-size:.75rem;
      color:var(--muted); background:var(--paper);
    }}
    footer a {{ color:var(--muted); }}
    @media (max-width:640px) {{
      .nav {{ display:none; }}
      .hero.flow {{ min-height:auto; padding:56px var(--pad) 48px; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <a class="logo" href="#">{_e(nombre)}</a>
    <nav class="nav">
      <a href="#problema">Problema</a>
      <a href="#beneficios">Beneficios</a>
      <a href="#precio">Precio</a>
      <a href="#faq">FAQ</a>
    </nav>
  </header>

  <section class="hero flow" id="hero">
    <div class="inner">
      <div class="brand-hero">{_e(nombre)}</div>
      <h1>{_e(hero.get('titulo'))}</h1>
      <p class="sub">{_e(hero.get('bajada'))}</p>
      <a class="btn" href="#precio">{_e(hero.get('cta'))}</a>
    </div>
  </section>

  <div class="proof">
    <strong>{_e(social.get('cifra_o_logos'))}</strong>
    {" · " + _e(social.get("texto")) if social.get("texto") else ""}
  </div>

  <section id="problema" class="flow">
    <div class="inner">
      <h2>{_e(problem.get('headline'))}</h2>
      <ul class="dolores">{dolores}</ul>
      <p class="puente">{_e(problem.get('puente'))}</p>
    </div>
  </section>

  <section id="beneficios" class="flow band">
    <div class="inner">
      <h2>Lo que ganás</h2>
      <div class="bens">{bens}</div>
    </div>
  </section>

  {test_html}

  <section id="precio" class="flow">
    <div class="inner">
      <h2>Precio claro</h2>
      <div class="price-box">
        <p class="price">{_e(pricing.get('precio'))}</p>
        <ul class="incluye">{incluye}</ul>
        <a class="btn" href="#">{_e(pricing.get('cta'))}</a>
      </div>
    </div>
  </section>

  <section id="faq" class="flow band">
    <div class="inner">
      <h2>Preguntas frecuentes</h2>
      {faqs}
    </div>
  </section>

  <div class="cta-final" id="cta">
    <div class="inner">
      <h2>{_e(cta.get('headline'))}</h2>
      <p>{_e(cta.get('sub'))}</p>
      <a class="btn" href="#precio">{_e(cta.get('cta'))}</a>
    </div>
  </div>

  <footer>
    {_e(footer.get('marca') or nombre)}
    {" · " + _e(footer.get("contacto")) if footer.get("contacto") else ""}
    {" · " + legales}
    {" · " + redes_html if redes_html else ""}
  </footer>
</body>
</html>
"""


def run(input: dict[str, Any]) -> dict[str, Any]:
    brief = input["brief"]
    copy = input["copy"]
    llm: LLMClient = input["llm"]
    skill = load_skill("design_skill.md")
    html_out = _build_html(brief, copy)
    _ = (llm, skill)
    return {"html": html_out, "path_hint": "landing.html"}

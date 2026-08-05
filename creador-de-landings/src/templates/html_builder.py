"""Genera HTML de landing en segundos (plantillas + catálogo multi-producto)."""

from __future__ import annotations

from src.templates.common import (  # noqa: F401
    _catalog_block,
    _catalog_css,
    _e,
    _fonts,
    _palette_vars,
)


def build_html(brief: dict) -> str:
    estilo = (brief.get("estilo") or "editorial").lower()
    if estilo == "mockup":
        return _tpl_mockup(brief)
    if estilo == "oferta":
        return _tpl_oferta(brief)
    if estilo == "tienda":
        from src.templates.tienda import render_tienda

        return render_tienda(brief)
    return _tpl_editorial(brief)


def _tpl_editorial(b: dict) -> str:
    marca, producto, promesa, cta = b.get("marca"), b.get("producto"), b.get("promesa"), b.get("cta")
    benefits = b.get("beneficios") or []
    faqs = b.get("faq") or []
    ben_html = "".join(f"<li>{_e(x)}</li>" for x in benefits)
    faq_html = "".join(
        f"<details><summary>{_e(f.get('q'))}</summary><p>{_e(f.get('a'))}</p></details>" for f in faqs
    )
    n = len(b.get("productos") or [])
    sub = f"{_e(producto)} · {n} guías libro × rol" if n else f"{_e(producto)} · Para {_e(b.get('cliente'))}"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(marca)} — {_e(producto)}</title>
  <meta name="description" content="{_e(promesa or producto)}"/>
  {_fonts()}
  <style>
    :root {{ {_palette_vars(b)} --pad:clamp(18px,4vw,40px); --max:1100px; }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--paper); color:var(--ink); line-height:1.55; }}
    .hero {{
      min-height:100svh; color:#fff; display:flex; flex-direction:column; justify-content:flex-end;
      background:
        linear-gradient(105deg, rgba(8,10,14,.88) 0%, rgba(8,10,14,.45) 50%, rgba(8,10,14,.2) 100%),
        radial-gradient(ellipse at 70% 40%, #2a3544 0%, #0f1419 70%);
      padding: clamp(48px,10vh,96px) var(--pad);
      animation: fade .9s ease both;
    }}
    @keyframes fade {{ from {{ opacity:0; transform:translateY(16px); }} to {{ opacity:1; transform:none; }} }}
    .brand {{ font-family:"Cormorant Garamond",Georgia,serif; font-size:clamp(2.2rem,6vw,3.8rem); letter-spacing:.16em; font-weight:600; margin-bottom:18px; }}
    h1 {{ font-family:"Cormorant Garamond",Georgia,serif; font-weight:500; font-size:clamp(1.35rem,3vw,1.85rem); max-width:18ch; margin-bottom:12px; }}
    .sub {{ max-width:38ch; color:rgba(255,255,255,.78); margin-bottom:24px; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:50px; padding:0 28px; background:var(--accent); color:#fff; font-size:.72rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; text-decoration:none; border:none; }}
    .btn-dark {{ background:var(--ink); color:var(--paper); }}
    section {{ padding:clamp(48px,8vw,72px) var(--pad); max-width:var(--max); margin:0 auto; }}
    h2 {{ font-family:"Cormorant Garamond",Georgia,serif; font-weight:500; font-size:clamp(1.4rem,3vw,1.9rem); margin-bottom:20px; text-align:center; }}
    ul.benefits {{ list-style:none; padding:0; max-width:40ch; margin:0 auto 28px; }}
    ul.benefits li {{ padding:10px 0; border-bottom:1px solid #e7e1d8; color:var(--muted); }}
    details {{ background:#fff; border:1px solid #e7e1d8; padding:14px 16px; margin-bottom:10px; }}
    summary {{ cursor:pointer; font-weight:500; }}
    details p {{ margin-top:8px; color:var(--muted); font-size:.92rem; }}
    .cta-wrap {{ text-align:center; margin-top:28px; }}
    footer {{ text-align:center; padding:28px; font-size:.7rem; color:var(--muted); }}
    {_catalog_css()}
  </style>
</head>
<body>
  <section class="hero">
    <div class="brand">{_e(marca)}</div>
    <h1>{_e(promesa or producto)}</h1>
    <p class="sub">{sub}</p>
    <a class="btn" href="#guias">{_e(cta)}</a>
  </section>
  {_catalog_block(b)}
  <section id="incluye">
    <h2>Por qué estas guías</h2>
    <ul class="benefits">{ben_html}</ul>
  </section>
  <section>
    <h2>Preguntas frecuentes</h2>
    {faq_html}
    <div class="cta-wrap"><a class="btn btn-dark" href="#guias">{_e(cta)}</a></div>
  </section>
  <footer>Generado con creador-de-landings · cursorprime</footer>
</body>
</html>
"""


def _tpl_mockup(b: dict) -> str:
    marca, producto, promesa, cta = b.get("marca"), b.get("producto"), b.get("promesa"), b.get("cta")
    benefits = "".join(f"<li>{_e(x)}</li>" for x in (b.get("beneficios") or []))
    n = len(b.get("productos") or [])
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(marca)}</title>
  {_fonts()}
  <style>
    :root {{ {_palette_vars(b)} --bg:var(--paper); --pad:clamp(16px,4vw,36px); --max:1100px; }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ padding:20px var(--pad); text-align:center; font-family:"Cormorant Garamond",serif; letter-spacing:.14em; font-size:1.2rem; }}
    .hero {{ display:grid; grid-template-columns:1.1fr .9fr; gap:32px; max-width:var(--max); margin:0 auto; padding:clamp(32px,6vw,64px) var(--pad); align-items:center; }}
    .mock {{
      aspect-ratio:4/3; background:linear-gradient(145deg,#1e293b,#0f172a); border-radius:12px;
      display:flex; align-items:center; justify-content:center; color:#fff; font-family:"Cormorant Garamond",serif;
      font-size:1.2rem; letter-spacing:.08em; box-shadow:0 24px 60px rgba(0,0,0,.18); text-align:center; padding:20px;
    }}
    h1 {{ font-family:"Cormorant Garamond",serif; font-weight:500; font-size:clamp(1.6rem,3vw,2.2rem); margin-bottom:12px; }}
    .sub {{ color:var(--muted); margin-bottom:20px; max-width:36ch; }}
    .btn {{ display:inline-flex; min-height:48px; padding:0 24px; align-items:center; background:var(--ink); color:#fff; text-decoration:none; font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; font-weight:600; }}
    .btn-dark {{ background:var(--ink); color:#fff; }}
    section {{ padding:clamp(40px,7vw,64px) var(--pad); max-width:var(--max); margin:0 auto; }}
    h2 {{ font-family:"Cormorant Garamond",serif; font-weight:500; text-align:center; margin-bottom:20px; }}
    ul {{ margin:20px 0; padding-left:18px; color:var(--muted); }}
    {_catalog_css()}
    @media (max-width:800px) {{ .hero {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header>{_e(marca)}</header>
  <section class="hero">
    <div class="mock">{n} guías<br/>libro × rol</div>
    <div>
      <h1>{_e(promesa or producto)}</h1>
      <p class="sub">{_e(producto)} — elige tu oficio</p>
      <a class="btn" href="#guias">{_e(cta)}</a>
      <ul>{benefits}</ul>
    </div>
  </section>
  {_catalog_block(b)}
</body>
</html>
"""




def _tpl_oferta(b: dict) -> str:
    marca, producto, promesa, cta = b.get("marca"), b.get("producto"), b.get("promesa"), b.get("cta")
    benefits = "".join(f"<li>✓ {_e(x)}</li>" for x in (b.get("beneficios") or []))
    faqs = "".join(
        f"<div class='faq'><strong>{_e(f.get('q'))}</strong><p>{_e(f.get('a'))}</p></div>"
        for f in (b.get("faq") or [])
    )
    n = len(b.get("productos") or [])
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(marca)} — Colección</title>
  {_fonts()}
  <style>
    :root {{ {_palette_vars(b)} --bg:var(--paper); --soft:color-mix(in srgb, var(--paper) 88%, var(--muted)); --pad:20px; --max:960px; }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--bg); color:var(--ink); }}
    .hero {{ background:var(--soft); padding:clamp(40px,8vw,72px) 20px; text-align:center; }}
    .brand {{ font-size:.75rem; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin-bottom:12px; }}
    h1 {{ font-family:"Cormorant Garamond",serif; font-size:clamp(1.8rem,4vw,2.6rem); max-width:18ch; margin:0 auto 14px; line-height:1.15; }}
    .sub {{ color:var(--muted); max-width:40ch; margin:0 auto 22px; }}
    .btn {{ display:inline-flex; min-height:52px; padding:0 32px; background:var(--accent); color:#fff; text-decoration:none; font-weight:600; letter-spacing:.08em; text-transform:uppercase; font-size:.75rem; align-items:center; justify-content:center; }}
    .btn-dark {{ background:var(--ink); color:var(--paper); }}
    section {{ max-width:var(--max); margin:0 auto; padding:40px 20px; }}
    h2 {{ font-family:"Cormorant Garamond",serif; text-align:center; margin-bottom:18px; }}
    ul {{ list-style:none; padding:0; max-width:480px; margin:0 auto; }}
    ul li {{ padding:12px 0; border-bottom:1px solid #eee; }}
    .faq {{ background:var(--soft); padding:16px; margin-bottom:10px; }}
    .faq p {{ color:var(--muted); margin-top:6px; font-size:.92rem; }}
    .sticky {{ position:sticky; bottom:0; background:#fff; border-top:1px solid #eee; padding:14px; text-align:center; }}
    {_catalog_css()}
  </style>
</head>
<body>
  <section class="hero">
    <p class="brand">{_e(marca)}</p>
    <h1>{_e(promesa or producto)}</h1>
    <p class="sub">{n} guías · elige libro × tu rol</p>
    <a class="btn" href="#guias">{_e(cta)}</a>
  </section>
  {_catalog_block(b)}
  <section>
    <ul>{benefits}</ul>
  </section>
  <section id="faq">{faqs}</section>
  <div class="sticky"><a class="btn" href="#guias">{_e(cta)}</a></div>
</body>
</html>
"""

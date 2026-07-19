"""Genera HTML de landing en segundos (3 plantillas + catálogo multi-producto)."""

from __future__ import annotations

import html
import json
from typing import Any


def _e(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def build_html(brief: dict) -> str:
    estilo = (brief.get("estilo") or "editorial").lower()
    if estilo == "mockup":
        return _tpl_mockup(brief)
    if estilo == "oferta":
        return _tpl_oferta(brief)
    if estilo == "tienda":
        return _tpl_tienda(brief)
    return _tpl_editorial(brief)


def _fonts() -> str:
    return (
        '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600'
        '&family=Outfit:wght@400;500;600&display=swap" rel="stylesheet"/>'
    )


def _catalog_block(b: dict) -> str:
    productos = b.get("productos") or []
    roles = b.get("roles") or []
    serie = b.get("serie_libros") or []
    if not productos:
        return ""

    chips = ['<button type="button" class="role-chip is-active" data-rol="todos">Todos</button>']
    for r in roles:
        chips.append(
            f'<button type="button" class="role-chip" data-rol="{_e(r.get("slug"))}">{_e(r.get("nombre"))}</button>'
        )

    cards = []
    for p in productos:
        disp = bool(p.get("disponible"))
        opacity = "" if disp else ' style="opacity:0.55"'
        badge = "Disponible" if disp else "Próximamente"
        precio = p.get("precio") or "—"
        btn = (
            f'<a class="btn btn-dark btn-block" href="#">Añadir al carrito</a>'
            if disp
            else '<span class="btn btn-outline btn-block">Avísame</span>'
        )
        cards.append(
            f"""
      <article class="card" data-rol-card="{_e(p.get('rol'))}"{opacity}>
        <div class="card-cover">{_e(badge)}</div>
        <div class="card-body">
          <p class="card-brand">{_e(b.get('marca'))} · PDF</p>
          <h3>{_e(p.get('titulo'))}</h3>
          <p class="price">{_e(precio)}</p>
          {btn}
        </div>
      </article>"""
        )

    serie_line = " · ".join(_e(s.get("titulo", s.get("slug"))) for s in serie[:5])
    return f"""
  <section id="guias">
    <h2>Guías para tu rol</h2>
    <p class="serie-line">Serie: {serie_line}</p>
    <div class="role-filters" id="roleFilters">{"".join(chips)}</div>
    <div class="grid" id="guiasGrid">{"".join(cards)}</div>
  </section>
  <script>
  (function() {{
    const chips = document.querySelectorAll('.role-chip');
    const cards = document.querySelectorAll('[data-rol-card]');
    chips.forEach(chip => chip.addEventListener('click', () => {{
      chips.forEach(c => c.classList.remove('is-active'));
      chip.classList.add('is-active');
      const rol = chip.dataset.rol;
      cards.forEach(card => {{
        card.hidden = !(rol === 'todos' || card.dataset.rolCard === rol);
      }});
    }}));
  }})();
  </script>
"""


def _catalog_css() -> str:
    return """
    .serie-line { text-align:center; color:var(--muted); font-size:.85rem; margin:-8px 0 20px; }
    .role-filters { display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-bottom:28px; }
    .role-chip {
      padding:10px 16px; border:1px solid #e7e1d8; background:#fff; font-size:.72rem;
      letter-spacing:.06em; text-transform:uppercase; cursor:pointer; color:var(--muted); border-radius:999px;
    }
    .role-chip.is-active { background:var(--ink); color:#fff; border-color:var(--ink); }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr)); gap:20px; }
    .card { background:#fff; border:1px solid #e7e1d8; display:flex; flex-direction:column; }
    .card-cover {
      aspect-ratio:3/4; background:#efeae3; display:flex; align-items:center; justify-content:center;
      color:var(--muted); font-size:.8rem; letter-spacing:.08em; text-transform:uppercase;
    }
    .card-body { padding:18px; text-align:center; flex:1; display:flex; flex-direction:column; }
    .card-brand { font-size:.62rem; letter-spacing:.12em; color:var(--muted); text-transform:uppercase; margin-bottom:8px; }
    .card h3 { font-family:"Cormorant Garamond",Georgia,serif; font-size:1.05rem; font-weight:500; line-height:1.35; margin-bottom:10px; flex:1; }
    .price { font-size:1.05rem; font-weight:600; margin-bottom:14px; }
    .btn-block { width:100%; }
    .btn-outline { background:transparent; color:var(--ink); border:1px solid var(--ink); display:inline-flex; align-items:center; justify-content:center; min-height:48px; font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; }
    .card[hidden] { display:none !important; }
"""


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
    :root {{ --ink:#0f1419; --paper:#f7f4ef; --muted:#8a847c; --pad:clamp(18px,4vw,40px); --max:1100px; }}
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
    .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:50px; padding:0 28px; background:#fff; color:var(--ink); font-size:.72rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; text-decoration:none; border:none; }}
    .btn-dark {{ background:var(--ink); color:#fff; }}
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
    :root {{ --ink:#14110f; --bg:#faf6f0; --muted:#6a635c; --pad:clamp(16px,4vw,36px); --max:1100px; }}
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


def _tpl_tienda(b: dict) -> str:
    """Estilo inspirado en landings tipo Filjós: barra, colección, bestsellers, historia, newsletter."""
    marca = b.get("marca")
    producto = b.get("producto")
    promesa = b.get("promesa")
    cta = b.get("cta")
    productos = b.get("productos") or []
    roles = b.get("roles") or []
    historia = b.get("historia") or (
        f"{marca} aplica ideas de grandes libros a tu oficio. "
        "Elige libro × rol y baja la guía lista para usar."
    )
    barra = b.get("barra_aviso") or "Colección de guías · PDF al instante"
    mision = b.get("mision") or ""
    testimonios = b.get("testimonios") or []

    disponible = next((p for p in productos if p.get("disponible")), productos[0] if productos else None)
    nuevo_titulo = (disponible or {}).get("titulo") or producto
    nuevo_precio = (disponible or {}).get("precio") or b.get("precio") or ""

    nav = ['<a href="#guias">Colección</a>']
    for r in roles[:6]:
        nav.append(f'<a href="#guias" data-nav-rol="{_e(r.get("slug"))}">{_e(r.get("nombre"))}</a>')
    nav.append('<a href="#historia">Marca</a>')

    best = []
    for p in productos[:8]:
        disp = bool(p.get("disponible"))
        badge = "Disponible" if disp else "Próximamente"
        btn = (
            '<a class="btn btn-dark btn-block" href="#">Añadir al carrito</a>'
            if disp
            else '<span class="btn btn-outline btn-block">Avísame</span>'
        )
        best.append(
            f"""
      <article class="card" data-rol-card="{_e(p.get('rol'))}"{' style="opacity:0.55"' if not disp else ''}>
        <div class="card-cover">{badge}</div>
        <div class="card-body">
          <p class="card-brand">{_e(marca)} · PDF</p>
          <h3>{_e(p.get('titulo'))}</h3>
          <p class="price">{_e(p.get('precio') or '—')}</p>
          {btn}
        </div>
      </article>"""
        )

    chips = ['<button type="button" class="role-chip is-active" data-rol="todos">Todos</button>']
    for r in roles:
        chips.append(
            f'<button type="button" class="role-chip" data-rol="{_e(r.get("slug"))}">{_e(r.get("nombre"))}</button>'
        )

    testi_html = ""
    for t in testimonios[:4]:
        texto = t.get("texto") or ""
        if "[PENDIENTE" in texto:
            continue
        testi_html += (
            f'<blockquote class="quote"><p>{_e(texto)}</p>'
            f"<cite>— {_e(t.get('autor') or 'Cliente')}</cite></blockquote>"
        )
    if not testi_html:
        testi_html = (
            '<p class="muted center">Cuando tengamos reseñas reales, aparecen aquí. '
            "No inventamos testimonios.</p>"
        )

    mision_html = ""
    if mision:
        mision_html = f"""
  <section id="mision" class="band">
    <h2>Por qué importa</h2>
    <p class="story">{_e(mision)}</p>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(marca)} — Colección</title>
  <meta name="description" content="{_e(promesa or producto)}"/>
  {_fonts()}
  <style>
    :root {{
      --ink:#12151a; --paper:#f6f3ee; --sand:#ebe6de; --muted:#7a746c;
      --pad:clamp(16px,4vw,40px); --max:1120px;
    }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--paper); color:var(--ink); line-height:1.55; }}
    .announce {{
      background:var(--ink); color:#f4f0ea; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase;
      text-align:center; padding:10px var(--pad);
    }}
    .top {{
      display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px;
      padding:14px var(--pad); border-bottom:1px solid #e4dfd6; background:rgba(246,243,238,.92);
      position:sticky; top:0; z-index:5; backdrop-filter:blur(8px);
    }}
    .logo {{
      font-family:"Cormorant Garamond",Georgia,serif; font-size:clamp(1.5rem,3vw,2rem);
      letter-spacing:.18em; font-weight:600; text-decoration:none; color:var(--ink);
    }}
    .nav {{ display:flex; flex-wrap:wrap; gap:14px; }}
    .nav a {{ color:var(--muted); text-decoration:none; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; }}
    .nav a:hover {{ color:var(--ink); }}
    .hero-nuevo {{
      min-height:min(88svh,760px); display:grid; grid-template-columns:1.05fr .95fr; gap:0;
      background:
        linear-gradient(120deg, rgba(12,14,18,.9) 0%, rgba(12,14,18,.35) 55%, rgba(12,14,18,.15) 100%),
        radial-gradient(ellipse at 75% 35%, #314155 0%, #12151a 70%);
      color:#fff; animation: rise .85s ease both;
    }}
    @keyframes rise {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
    .hero-copy {{ padding:clamp(40px,10vh,96px) var(--pad); display:flex; flex-direction:column; justify-content:flex-end; max-width:34rem; }}
    .eyebrow {{ font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; color:rgba(255,255,255,.65); margin-bottom:14px; }}
    .hero-copy h1 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:clamp(1.6rem,3.6vw,2.35rem); max-width:16ch; margin-bottom:12px; line-height:1.15;
    }}
    .hero-copy .sub {{ color:rgba(255,255,255,.78); margin-bottom:10px; max-width:36ch; }}
    .hero-copy .price-lg {{ font-size:1.15rem; font-weight:600; margin-bottom:22px; }}
    .hero-visual {{
      display:flex; align-items:center; justify-content:center; padding:var(--pad);
      font-family:"Cormorant Garamond",Georgia,serif; letter-spacing:.12em; font-size:clamp(1.4rem,3vw,2rem);
      color:rgba(255,255,255,.35); text-align:center;
    }}
    .btn {{
      display:inline-flex; align-items:center; justify-content:center; min-height:50px; padding:0 26px;
      background:#fff; color:var(--ink); font-size:.72rem; font-weight:600; letter-spacing:.12em;
      text-transform:uppercase; text-decoration:none; border:none; cursor:pointer;
    }}
    .btn-dark {{ background:var(--ink); color:#fff; }}
    .btn-outline {{
      background:transparent; color:var(--ink); border:1px solid var(--ink);
      display:inline-flex; align-items:center; justify-content:center; min-height:48px;
      font-size:.72rem; letter-spacing:.1em; text-transform:uppercase;
    }}
    .btn-block {{ width:100%; }}
    section {{ padding:clamp(48px,8vw,80px) var(--pad); max-width:var(--max); margin:0 auto; }}
    section.band {{ max-width:none; background:var(--sand); }}
    section.band > * {{ max-width:var(--max); margin-left:auto; margin-right:auto; }}
    h2 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:clamp(1.45rem,3vw,2rem); margin-bottom:22px; text-align:center;
    }}
    .story {{ max-width:48ch; margin:0 auto; text-align:center; color:var(--muted); }}
    .center {{ text-align:center; }}
    .muted {{ color:var(--muted); }}
    .quotes {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; }}
    .quote {{ background:#fff; border:1px solid #e4dfd6; padding:20px; }}
    .quote p {{ font-size:.95rem; margin-bottom:12px; }}
    .quote cite {{ font-style:normal; font-size:.75rem; color:var(--muted); letter-spacing:.04em; }}
    .news {{
      text-align:center; padding:clamp(48px,8vw,72px) var(--pad);
      background:var(--ink); color:#f4f0ea;
    }}
    .news h2 {{ color:#f4f0ea; }}
    .news p {{ color:rgba(244,240,234,.72); max-width:36ch; margin:0 auto 20px; }}
    .news .btn {{ background:#f4f0ea; color:var(--ink); }}
    footer {{ text-align:center; padding:28px; font-size:.7rem; color:var(--muted); }}
    {_catalog_css()}
    @media (max-width:860px) {{
      .hero-nuevo {{ grid-template-columns:1fr; min-height:auto; }}
      .hero-visual {{ min-height:220px; order:-1; }}
    }}
  </style>
</head>
<body>
  <div class="announce">{_e(barra)}</div>
  <div class="top">
    <a class="logo" href="#">{_e(marca)}</a>
    <nav class="nav">{"".join(nav)}</nav>
  </div>

  <section class="hero-nuevo">
    <div class="hero-copy">
      <p class="eyebrow">Ahora nuevo</p>
      <div class="logo" style="color:#fff;margin-bottom:16px;font-size:clamp(2rem,5vw,3rem)">{_e(marca)}</div>
      <h1>{_e(nuevo_titulo)}</h1>
      <p class="sub">{_e(promesa or producto)}</p>
      <p class="price-lg">{_e(nuevo_precio)}</p>
      <a class="btn" href="#guias">{_e(cta)}</a>
    </div>
    <div class="hero-visual">Colección<br/>libro × rol</div>
  </section>

  <section id="guias">
    <h2>Bestsellers</h2>
    <div class="role-filters" id="roleFilters">{"".join(chips)}</div>
    <div class="grid" id="guiasGrid">{"".join(best)}</div>
  </section>

  <section id="historia" class="band">
    <h2>La marca</h2>
    <p class="story">{_e(historia)}</p>
    <p class="center" style="margin-top:22px"><a class="btn btn-dark" href="#guias">Ver toda la colección</a></p>
  </section>

  <section>
    <h2>Lo que dicen</h2>
    <div class="quotes">{testi_html}</div>
  </section>
  {mision_html}

  <div class="news" id="newsletter">
    <h2>10% en tu primera guía</h2>
    <p>Suscríbete al newsletter. Te avisamos cuando salgan nuevas combinaciones libro × rol.</p>
    <a class="btn" href="#guias">Quiero el descuento</a>
  </div>

  <footer>Generado con creador-de-landings · estilo tienda (ref. estructura tipo Filjós)</footer>
  <script>
  (function() {{
    const chips = document.querySelectorAll('.role-chip');
    const cards = document.querySelectorAll('[data-rol-card]');
    const filter = (rol) => {{
      chips.forEach(c => c.classList.toggle('is-active', c.dataset.rol === rol));
      cards.forEach(card => {{
        card.hidden = !(rol === 'todos' || card.dataset.rolCard === rol);
      }});
    }};
    chips.forEach(chip => chip.addEventListener('click', () => filter(chip.dataset.rol)));
    document.querySelectorAll('[data-nav-rol]').forEach(a => {{
      a.addEventListener('click', (e) => {{ e.preventDefault(); filter(a.dataset.navRol); location.hash = 'guias'; }});
    }});
  }})();
  </script>
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
    :root {{ --ink:#111; --accent:#0f1419; --bg:#fff; --soft:#f3f1ec; --muted:#666; --pad:20px; --max:960px; }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--bg); color:var(--ink); }}
    .hero {{ background:var(--soft); padding:clamp(40px,8vw,72px) 20px; text-align:center; }}
    .brand {{ font-size:.75rem; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin-bottom:12px; }}
    h1 {{ font-family:"Cormorant Garamond",serif; font-size:clamp(1.8rem,4vw,2.6rem); max-width:18ch; margin:0 auto 14px; line-height:1.15; }}
    .sub {{ color:var(--muted); max-width:40ch; margin:0 auto 22px; }}
    .btn {{ display:inline-flex; min-height:52px; padding:0 32px; background:var(--accent); color:#fff; text-decoration:none; font-weight:600; letter-spacing:.08em; text-transform:uppercase; font-size:.75rem; align-items:center; justify-content:center; }}
    .btn-dark {{ background:var(--ink); color:#fff; }}
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

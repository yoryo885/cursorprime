"""Plantilla estilo tienda (colección multiproducto)."""

from __future__ import annotations

from src.templates.common import (
    _catalog_css,
    _e,
    _fonts,
    _palette_vars,
    resolve_hero_imagen,
)

def render_tienda(b: dict) -> str:
    """Landing tienda con copy profesional de marketing + colección multiproducto."""
    marca = b.get("marca")
    producto = b.get("producto")
    promesa = b.get("promesa")
    cta = b.get("cta")
    productos = b.get("productos") or []
    roles = b.get("roles") or []
    serie = b.get("serie_libros") or []
    historia = b.get("historia") or ""
    mision = b.get("mision") or ""
    barra = b.get("barra_aviso") or ""
    hero_eyebrow = b.get("hero_eyebrow") or "Colección profesional"
    hero_titulo = b.get("hero_titulo") or f"{marca}: guías para tu rol"
    hero_sub = b.get("hero_sub") or promesa or producto
    hero_badge = b.get("hero_badge_calidad") or ""
    precio = b.get("precio") or ""
    calidad = b.get("calidad") or []
    incluye = b.get("incluye") or []
    faqs = b.get("faq") or []
    n_disp = sum(1 for p in productos if p.get("disponible"))
    n_prox = len(productos) - n_disp

    disponible = next((p for p in productos if p.get("disponible")), None)
    spotlight = (disponible or {}).get("titulo") or ""

    # Slides por rol: libro visual + disponibles / próximamente
    libros_by = {s.get("slug"): s for s in serie}
    role_slides = []
    for r in roles:
        slug = r.get("slug")
        guías_rol = [p for p in productos if p.get("rol") == slug]
        d = sum(1 for p in guías_rol if p.get("disponible"))
        pr = len(guías_rol) - d
        if not guías_rol:
            continue
        guia = next((p for p in guías_rol if p.get("disponible")), guías_rol[0])
        libro = libros_by.get(guia.get("libro"), {})
        role_slides.append(
            {
                "slug": slug,
                "nombre": r.get("nombre"),
                "disp": d,
                "prox": pr,
                "guia": guia.get("titulo"),
                "libro_slug": guia.get("libro") or "pareto",
                "libro_titulo": libro.get("titulo") or guia.get("titulo"),
                "libro_autor": libro.get("autor") or "",
                "disponible": bool(guia.get("disponible")),
            }
        )
    # slide resumen: libro destacado
    featured = disponible or (productos[0] if productos else {})
    feat_libro = libros_by.get((featured or {}).get("libro"), {})
    slides_data = [
        {
            "slug": "todos",
            "nombre": "Toda la colección",
            "disp": n_disp,
            "prox": n_prox,
            "guia": spotlight or "Guías libro × rol",
            "libro_slug": (featured or {}).get("libro") or "pareto",
            "libro_titulo": feat_libro.get("titulo") or "Colección Vértice Pro",
            "libro_autor": feat_libro.get("autor") or marca,
            "disponible": True,
        },
        *role_slides,
    ]

    def _book_cover(s: dict, size: str = "") -> str:
        theme = {
            "pareto": ("#3d4f5c", "#d8c4a0", "80/20"),
            "habitos": ("#4a5c48", "#c9d4b8", "1%"),
            "kahneman": ("#4a3f55", "#cbb8d4", "pensar"),
        }.get(s.get("libro_slug") or "pareto", ("#3d4f5c", "#d8c4a0", "guía"))
        bg, accent, mark = theme
        estado = "Disponible" if s.get("disponible") else "Próximamente"
        cls = "book book-hero" if size == "hero" else "book"
        return f"""
          <div class="{cls}" style="--book-bg:{bg}; --book-accent:{accent}">
            <div class="book-spine"></div>
            <div class="book-front">
              <p class="book-series">{_e(marca)}</p>
              <p class="book-mark">{_e(mark)}</p>
              <p class="book-title">{_e(s.get('libro_titulo') or '')}</p>
              <p class="book-author">{_e(s.get('libro_autor') or '')}</p>
              <div class="book-footer">
                <p class="book-rol">{_e(s.get('nombre') or '')}</p>
                <p class="book-estado">{_e(estado)}</p>
              </div>
            </div>
          </div>"""

    slides_html = []
    dots_html = []
    for i, s in enumerate(slides_data):
        active = " is-active" if i == 0 else ""
        disp_label = "disponible" if s["disp"] == 1 else "disponibles"
        slides_html.append(
            f"""
        <div class="role-slide{active}" data-slide="{i}" data-rol-slide="{_e(s['slug'])}" aria-hidden="{'false' if i == 0 else 'true'}">
          {_book_cover(s, size="hero")}
          <div class="slide-caption">
            <p class="slide-count"><strong>{s['disp']}</strong> {disp_label} · +{s['prox']} próximamente</p>
            <p class="slide-guia">{_e(s.get('guia') or '')}</p>
          </div>
        </div>"""
        )
        dots_html.append(
            f'<button type="button" class="role-dot{active}" data-dot="{i}" aria-label="{_e(s.get("nombre") or f"Guía {i+1}")}"></button>'
        )

    nav = [
        '<a href="#guias">Colección</a>',
        '<a href="#historia">Marca</a>',
        '<a href="#faq">FAQ</a>',
    ]
    hero_imagen = resolve_hero_imagen(b.get("hero_imagen") or "")

    best = []
    libros_by_card = {s.get("slug"): s for s in serie}
    for p in productos:
        disp = bool(p.get("disponible"))
        badge = p.get("badge_marketing") or ("Disponible ahora" if disp else "Próximamente")
        btn = (
            f'<a class="btn btn-dark btn-block" href="#">Comprar · {_e(p.get("precio") or "")}</a>'
            if disp
            else '<span class="btn btn-outline btn-block">Avísame al lanzar</span>'
        )
        sub = p.get("subtitulo") or ""
        libro = libros_by_card.get(p.get("libro"), {})
        theme = {
            "pareto": ("#3d4f5c", "#d8c4a0", "80/20"),
            "habitos": ("#4a5c48", "#c9d4b8", "1%"),
            "kahneman": ("#4a3f55", "#cbb8d4", "pensar"),
        }.get(p.get("libro") or "pareto", ("#3d4f5c", "#d8c4a0", "guía"))
        bg, accent, mark = theme
        rol_nombre = next(
            (r.get("nombre") for r in roles if r.get("slug") == p.get("rol")),
            p.get("rol") or "",
        )
        best.append(
            f"""
      <article class="card guia-card" data-rol-card="{_e(p.get('rol'))}" data-disp="{1 if disp else 0}">
        <div class="card-cover-wrap">
          <div class="book book-card" style="--book-bg:{bg}; --book-accent:{accent}">
            <div class="book-spine"></div>
            <div class="book-front">
              <p class="book-mark">{_e(mark)}</p>
              <p class="book-title">{_e(libro.get('titulo') or p.get('titulo'))}</p>
              <p class="book-rol">{_e(rol_nombre)}</p>
            </div>
          </div>
        </div>
        <div class="card-body">
          <p class="card-brand">{_e(badge)}</p>
          <h3>{_e(p.get('titulo'))}</h3>
          <p class="card-sub">{_e(sub)}</p>
          <p class="price">{_e(p.get('precio') or '—')}</p>
          {btn}
        </div>
      </article>"""
        )

    chips = ['<button type="button" class="role-chip is-active" data-rol="todos">Todos los roles</button>']
    for r in roles:
        chips.append(
            f'<button type="button" class="role-chip" data-rol="{_e(r.get("slug"))}">{_e(r.get("nombre"))}</button>'
        )

    calidad_html = "".join(
        f'<article class="pillar"><h3>{_e(c.get("titulo"))}</h3><p>{_e(c.get("texto"))}</p></article>'
        for c in calidad[:3]
    )
    faq_html = "".join(
        f"<details><summary>{_e(f.get('q'))}</summary><p>{_e(f.get('a'))}</p></details>"
        for f in faqs[:4]
    )
    hero_bg = (
        f"background-image:linear-gradient(115deg, rgba(27,34,44,.88), rgba(27,34,44,.72)),"
        f"url('{_e(hero_imagen)}'); background-size:cover; background-position:center;"
        if hero_imagen
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_e(marca)} — Colección profesional de guías</title>
  <meta name="description" content="{_e(promesa or producto)}"/>
  {_fonts()}
  <style>
    :root {{
      {_palette_vars(b)} --sand:color-mix(in srgb, var(--paper) 85%, var(--muted));
      --gold:#c9a962; --pad:clamp(16px,4vw,40px); --max:1120px;
    }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Outfit,system-ui,sans-serif; background:var(--paper); color:var(--ink); line-height:1.55; }}
    .announce {{
      background:var(--hero); color:#f0ebe3; font-size:.68rem; letter-spacing:.08em; text-transform:uppercase;
      text-align:center; padding:10px var(--pad);
    }}
    .top {{
      display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px;
      padding:14px var(--pad); border-bottom:1px solid #e4dfd6; background:color-mix(in srgb, var(--paper) 92%, transparent);
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
      min-height:min(78svh,680px); display:grid; grid-template-columns:1.05fr .95fr; gap:0;
      {hero_bg or (
        "background:linear-gradient(115deg, color-mix(in srgb, var(--hero) 96%, #fff) 0%,"
        " color-mix(in srgb, var(--hero) 88%, #3a4555) 45%,"
        " color-mix(in srgb, var(--hero) 92%, #4a5565) 100%);"
      )}
      color:#e8e4dc; animation: rise .85s ease both;
    }}
    @keyframes rise {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
    .hero-copy {{ padding:clamp(40px,10vh,96px) var(--pad); display:flex; flex-direction:column; justify-content:flex-end; max-width:36rem; }}
    .eyebrow {{ font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; color:rgba(232,228,220,.65); margin-bottom:14px; }}
    .hero-copy .brand-hero {{
      font-family:"Cormorant Garamond",Georgia,serif; letter-spacing:.18em; font-weight:600;
      font-size:clamp(2.2rem,5.5vw,3.6rem); margin-bottom:14px; color:#f0ebe3;
    }}
    .hero-copy h1 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:clamp(1.35rem,2.8vw,1.75rem); max-width:22ch; margin-bottom:14px; line-height:1.2;
      color:#f0ebe3;
    }}
    .hero-copy .sub {{ color:rgba(232,228,220,.82); margin-bottom:14px; max-width:42ch; font-size:.98rem; }}
    .hero-copy .badge-q {{
      font-size:.72rem; letter-spacing:.06em; color:rgba(232,228,220,.68); margin-bottom:18px; max-width:40ch;
    }}
    .hero-copy .price-lg {{ font-size:1.05rem; font-weight:600; margin-bottom:20px; color:#f0ebe3; }}
    .hero-visual {{
      position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center;
      padding:clamp(28px,5vw,48px) var(--pad) clamp(20px,4vw,36px);
      min-height:520px;
      background:
        radial-gradient(ellipse at 50% 40%, #2f3a48 0%, var(--hero) 68%);
      overflow:hidden;
    }}
    .role-carousel {{
      position:relative; width:min(100%,340px); height:390px; margin:0 auto;
    }}
    .role-slide {{
      position:absolute; inset:0; display:flex; flex-direction:column;
      align-items:center; justify-content:center; gap:18px;
      opacity:0; visibility:hidden;
      transform:scale(.92) translateY(12px);
      transition:opacity .5s ease, transform .5s ease, visibility .5s;
      pointer-events:none;
    }}
    .role-slide.is-active {{
      opacity:1; visibility:visible; transform:scale(1) translateY(0);
      pointer-events:auto; z-index:2;
    }}
    .book {{
      position:relative; width:148px; height:210px; flex-shrink:0;
      transform:perspective(900px) rotateY(-14deg) rotateX(3deg);
      filter:drop-shadow(0 22px 32px rgba(0,0,0,.5));
    }}
    .book-hero {{
      width:200px; height:290px;
      transform:perspective(900px) rotateY(-16deg) rotateX(4deg);
      animation: bookIn .7s ease both;
    }}
    @keyframes bookIn {{
      from {{ opacity:0; transform:perspective(900px) rotateY(-28deg) translateY(18px); }}
      to {{ opacity:1; transform:perspective(900px) rotateY(-16deg) rotateX(4deg); }}
    }}
    .book-spine {{
      position:absolute; left:0; top:8px; bottom:8px; width:16px;
      background:linear-gradient(90deg, #0a0e14, color-mix(in srgb, var(--book-bg) 65%, #000));
      border-radius:3px 0 0 3px;
      box-shadow:inset -2px 0 4px rgba(0,0,0,.35);
    }}
    .book-front {{
      position:absolute; left:14px; right:0; top:0; bottom:0;
      background:
        linear-gradient(165deg, color-mix(in srgb, var(--book-bg) 92%, #fff) 0%, var(--book-bg) 48%, color-mix(in srgb, var(--book-bg) 75%, #000) 100%);
      border:1px solid color-mix(in srgb, var(--book-accent) 40%, transparent);
      border-radius:0 5px 5px 0;
      padding:20px 16px 18px;
      display:flex; flex-direction:column;
      color:var(--book-accent);
    }}
    .book-hero .book-front {{ padding:24px 18px 20px; }}
    .book-series {{
      font-size:.58rem; letter-spacing:.2em; text-transform:uppercase;
      color:rgba(240,235,227,.55); margin-bottom:10px;
    }}
    .book-mark {{
      font-size:.62rem; letter-spacing:.18em; text-transform:uppercase; opacity:.75; margin-bottom:14px;
      color:var(--book-accent);
    }}
    .book-title {{
      font-family:"Cormorant Garamond",Georgia,serif; font-size:1.05rem; font-weight:600;
      line-height:1.2; letter-spacing:.02em; flex:1; color:#f5f0e8;
    }}
    .book-hero .book-title {{ font-size:1.35rem; }}
    .book-author {{ font-size:.7rem; letter-spacing:.04em; opacity:.8; margin-top:12px; color:#e8e0d4; }}
    .book-footer {{
      margin-top:auto; padding-top:12px;
      border-top:1px solid color-mix(in srgb, var(--book-accent) 35%, transparent);
    }}
    .book-rol {{
      font-size:.62rem; letter-spacing:.12em; text-transform:uppercase;
      color:var(--book-accent); margin:0;
    }}
    .book-estado {{
      margin-top:6px; font-size:.62rem; letter-spacing:.08em; text-transform:uppercase;
      opacity:.7; color:#e8e0d4;
    }}
    .slide-caption {{ text-align:center; max-width:260px; }}
    .slide-count {{
      font-size:.78rem; letter-spacing:.04em; color:rgba(232,228,220,.78);
    }}
    .slide-count strong {{
      font-family:"Cormorant Garamond",Georgia,serif; font-size:1.15rem; font-weight:500; color:#f0ebe3;
    }}
    .slide-guia {{
      margin-top:6px; font-size:.78rem; color:rgba(216,210,200,.55); line-height:1.35;
    }}
    .carousel-nav {{
      display:flex; align-items:center; justify-content:center; gap:16px; margin-top:8px; width:100%;
      position:relative; z-index:3;
    }}
    .carousel-btn {{
      width:42px; height:42px; border:1px solid rgba(216,210,200,.4); background:rgba(0,0,0,.15);
      color:#d8d2c8; font-size:1.2rem; cursor:pointer; display:inline-flex; align-items:center; justify-content:center;
      transition:border-color .2s, background .2s;
    }}
    .carousel-btn:hover {{ border-color:rgba(216,210,200,.85); background:rgba(255,255,255,.06); }}
    .role-dots {{ display:flex; gap:8px; align-items:center; }}
    .role-dot {{
      width:7px; height:7px; border-radius:50%; border:none; padding:0; cursor:pointer;
      background:rgba(216,210,200,.28);
    }}
    .role-dot.is-active {{ background:#d8d2c8; }}
    @media (max-width:860px) {{
      .book-hero {{ width:170px; height:250px; transform:perspective(900px) rotateY(-8deg); }}
      .role-carousel {{ height:350px; }}
    }}
    .btn {{
      display:inline-flex; align-items:center; justify-content:center; min-height:50px; padding:0 26px;
      background:var(--gold); color:var(--ink); font-size:.72rem; font-weight:600; letter-spacing:.12em;
      text-transform:uppercase; text-decoration:none; border:none; cursor:pointer;
    }}
    .btn-dark {{ background:var(--ink); color:var(--paper); }}
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
      font-size:clamp(1.45rem,3vw,2rem); margin-bottom:12px; text-align:center;
    }}
    .sec-sub {{ text-align:center; color:var(--muted); max-width:48ch; margin:0 auto 28px; font-size:.95rem; }}
    .story {{ max-width:52ch; margin:0 auto; text-align:center; color:var(--muted); }}
    .center {{ text-align:center; }}
    .muted {{ color:var(--muted); }}
    .pillars {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:18px; margin-top:8px; }}
    .pillar {{ background:#fff; border:1px solid #e4dfd6; padding:22px 20px; }}
    .pillar h3 {{ font-family:"Cormorant Garamond",Georgia,serif; font-weight:500; font-size:1.15rem; margin-bottom:8px; }}
    .pillar p {{ color:var(--muted); font-size:.92rem; }}
    .incluye {{ max-width:40ch; margin:0 auto; list-style:none; padding:0; }}
    .incluye li {{ padding:12px 0; border-bottom:1px solid #e4dfd6; color:var(--muted); }}
    .guia-card .card-cover-wrap {{
      aspect-ratio:4/5; background:color-mix(in srgb, var(--paper) 88%, #dfe6ee);
      display:flex; align-items:center; justify-content:center; padding:24px 16px;
    }}
    .book-card {{
      width:120px; height:168px;
      transform:perspective(800px) rotateY(-10deg) rotateX(2deg);
      filter:drop-shadow(0 14px 22px rgba(0,0,0,.22));
    }}
    .book-card .book-title {{ font-size:.92rem; }}
    .guia-card h3 {{
      font-family:"Cormorant Garamond",Georgia,serif; font-weight:500;
      font-size:1.05rem; margin:8px 0 10px; line-height:1.25;
    }}
    .guia-card .price {{ font-size:1rem; font-weight:600; margin-bottom:12px; }}
    details {{ background:#fff; border:1px solid #e4dfd6; padding:14px 16px; margin-bottom:10px; }}
    summary {{ cursor:pointer; font-weight:500; }}
    details p {{ margin-top:8px; color:var(--muted); font-size:.92rem; }}
    .news {{
      text-align:center; padding:clamp(48px,8vw,72px) var(--pad);
      background:var(--hero); color:#f0ebe3;
    }}
    .news h2 {{ color:#f0ebe3; }}
    .news p {{ color:rgba(240,235,227,.72); max-width:38ch; margin:0 auto 20px; }}
    .news .btn {{ background:#f0ebe3; color:var(--ink); }}
    footer {{ text-align:center; padding:28px; font-size:.7rem; color:var(--muted); }}
    .hero-badge {{ display:inline-block; margin:12px 0 0; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:var(--gold); }}
    .hero-precio {{ margin:8px 0 0; font-size:.95rem; color:rgba(240,235,227,.85); }}
    .mision {{ margin-top:18px; font-style:italic; }}
    .incluye {{ max-width:40ch; margin:16px auto 0; list-style:none; padding:0; text-align:left; }}
    .incluye li {{ padding:12px 0; border-bottom:1px solid #e4dfd6; color:var(--muted); }}
    .card-sub {{ font-size:.78rem; color:var(--muted); line-height:1.4; margin-bottom:12px; }}
    {_catalog_css()}
    @media (max-width:860px) {{
      .hero-nuevo {{ grid-template-columns:1fr; min-height:auto; }}
      .hero-visual {{ min-height:280px; order:-1; }}
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
      <p class="eyebrow">{_e(hero_eyebrow)}</p>
      <div class="brand-hero">{_e(marca)}</div>
      <h1>{_e(hero_titulo)}</h1>
      <p class="sub">{_e(hero_sub)}</p>
      {f'<p class="hero-badge">{_e(hero_badge)}</p>' if hero_badge else ''}
      {f'<p class="hero-precio">{_e(precio)}</p>' if precio else ''}
      <a class="btn" href="#guias">{_e(cta)}</a>
    </div>
    <div class="hero-visual" id="roleHero">
      <div class="role-carousel" id="roleCarousel" aria-roledescription="carrusel" aria-label="Roles de la colección">
        {"".join(slides_html)}
      </div>
      <div class="carousel-nav">
        <button type="button" class="carousel-btn" id="rolePrev" aria-label="Rol anterior">‹</button>
        <div class="role-dots" id="roleDots">{"".join(dots_html)}</div>
        <button type="button" class="carousel-btn" id="roleNext" aria-label="Rol siguiente">›</button>
      </div>
    </div>
  </section>

  <section id="guias">
    <h2>{_e(b.get('catalogo_titulo') or 'Explora la colección')}</h2>
    <p class="sec-sub">{_e(b.get('catalogo_sub') or '')}</p>
    <div class="role-filters" id="roleFilters">{"".join(chips)}</div>
    <div class="grid" id="guiasGrid">{"".join(best)}</div>
  </section>

  <section id="historia" class="band">
    <h2>La marca</h2>
    <p class="story">{_e(historia)}</p>
    {f'<p class="story mision">{_e(mision)}</p>' if mision else ''}
    <div class="pillars" style="margin-top:32px">{calidad_html}</div>
    {f'<h3 style="text-align:center;margin-top:36px">{_e(b.get("incluye_titulo") or "Qué incluye")}</h3><ul class="incluye">{"".join(f"<li>{_e(x)}</li>" for x in incluye[:6])}</ul>' if incluye else ''}
    <p class="center" style="margin-top:28px"><a class="btn btn-dark" href="#guias">Ver toda la colección</a></p>
  </section>

  {'' if b.get('ocultar_faq') else f"""<section id="faq">
    <h2>Preguntas frecuentes</h2>
    <p class="sec-sub">{_e(b.get('social_proof_nota') or '')}</p>
    {faq_html}
  </section>"""}

  {'' if b.get('ocultar_newsletter') else f"""<div class="news" id="newsletter">
    <h2>{_e(b.get('newsletter_titulo') or 'Acceso anticipado')}</h2>
    <p>{_e(b.get('newsletter_sub') or '')}</p>
    <a class="btn" href="#guias">{_e(b.get('newsletter_cta') or cta)}</a>
  </div>"""}

  <footer>{_e(marca)} · Colección profesional de guías · PDF de calidad</footer>
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

    // Hero roles: auto 5s (independiente de #guias)
    const slides = Array.from(document.querySelectorAll('.role-slide'));
    const dots = Array.from(document.querySelectorAll('.role-dot'));
    const prev = document.getElementById('rolePrev');
    const next = document.getElementById('roleNext');
    if (!slides.length) return;
    let idx = 0;
    let timer = null;
    const INTERVAL = 5000;

    const show = (n) => {{
      idx = (n + slides.length) % slides.length;
      slides.forEach((s, i) => {{
        const on = i === idx;
        s.classList.toggle('is-active', on);
        s.setAttribute('aria-hidden', on ? 'false' : 'true');
        const book = s.querySelector('.book-hero');
        if (book && on) {{
          book.style.animation = 'none';
          void book.offsetWidth;
          book.style.animation = '';
        }}
      }});
      dots.forEach((d, i) => d.classList.toggle('is-active', i === idx));
    }};
    const restart = () => {{
      if (timer) clearInterval(timer);
      timer = setInterval(() => show(idx + 1), INTERVAL);
    }};
    prev && prev.addEventListener('click', () => {{ show(idx - 1); restart(); }});
    next && next.addEventListener('click', () => {{ show(idx + 1); restart(); }});
    dots.forEach(d => d.addEventListener('click', () => {{
      show(Number(d.dataset.dot) || 0); restart();
    }}));
    restart();
  }})();
  </script>
</body>
</html>
"""


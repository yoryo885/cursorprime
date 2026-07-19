"""Ensambla preview.html — layout limpio desktop + móvil."""

from __future__ import annotations

import json
import shutil
import zipfile
from html import escape
from pathlib import Path

from src.config import load_json, shopify_theme_src, slug_meta, slug_output
from src.types import AgentResult, PipelineContext


def _carousel_slides(ctx: PipelineContext) -> list[dict]:
    data = load_json(slug_meta(ctx.slug) / "assets.json", {}) or {}
    slides = data.get("carousel") or ctx.marca.get("serie_libros") or []
    if not slides:
        piloto = ctx.marca.get("producto_piloto", {})
        slides = [{"titulo": piloto.get("titulo", "Guía PDF"), "src": ctx.assets.get("portada", ""), "subtitulo": "Aplica en tu rol"}]
    return slides


def _catalogo_guias(ctx: PipelineContext) -> list[dict]:
    data = load_json(slug_meta(ctx.slug) / "assets.json", {}) or {}
    return data.get("catalogo_guias") or ctx.marca.get("catalogo_guias") or []


def _ux(ctx: PipelineContext) -> dict:
    return ctx.marca.get("ux_landing") or {}


def _guia_src(assets: dict, guia: dict, fallback: str) -> str:
    slug = guia.get("slug", "")
    return assets.get(f"portada_{slug}") or fallback


def _render_html(ctx: PipelineContext) -> str:
    c = ctx.copy
    m = ctx.marca
    col = m.get("colores", {})
    a = ctx.assets
    p = c.get("product", {})
    name = m.get("marca", "Vértice Pro").upper()
    portada = a.get("portada", "assets/portada-pareto.svg")
    mockup = a.get("mockup_movil", "assets/mockup-movil.svg")
    imagen_lectura = a.get("imagen_lectura", "")
    slides = _carousel_slides(ctx)
    catalogo = _catalogo_guias(ctx)
    roles = m.get("roles") or []
    serie = m.get("serie_libros") or []
    ux = _ux(ctx)
    cat = ux.get("copy_catalogo") or {}
    benefits = c.get("benefits") or cat.get("benefits") or []
    precio_display = m.get("precio_display", "$4.99")

    slides_html = ""
    dots_html = ""
    for i, s in enumerate(slides):
        active = " is-active" if i == 0 else ""
        soon = "" if s.get("disponible", True) else " is-soon"
        slug = s.get("slug", "")
        sub = s.get("subtitulo") or s.get("autor") or "Serie Aplicar en tu rol"
        slides_html += f"""
        <figure class="carousel-slide{active}{soon}" data-index="{i}" data-slug="{escape(str(slug))}" data-title="{escape(str(s.get('titulo','')))}" data-subtitle="{escape(str(sub))}">
          <img src="{escape(str(s.get('src', portada)))}" alt="{escape(str(s.get('titulo','')))}" draggable="false"/>
        </figure>"""
        dots_html += f'<button type="button" class="carousel-dot{" is-active" if i == 0 else ""}" data-index="{i}" aria-label="Libro {i+1}"></button>'

    carousel_json = json.dumps(slides, ensure_ascii=False).replace("</", "<\\/")
    first_sub = slides[0].get("subtitulo") or slides[0].get("autor") or "Elige tu rol abajo" if slides else ""

    hero_bullets = ux.get("hero_bullets") or []
    hero_bullets_html = ""
    for bullet in hero_bullets[:3]:
        hero_bullets_html += f"<li>{escape(str(bullet))}</li>"
    hero_title_em = cat.get("hero_title_em") or c.get("hero_title_em", "")
    hero_title = c.get("hero_title", cat.get("hero_title", ""))
    hero_title_html = escape(hero_title)
    if hero_title_em:
        hero_title_html += f'<br/><em class="hero-accent">{escape(hero_title_em)}</em>'
    hero_subtitle = c.get("hero_subtitle", cat.get("hero_subtitle", ""))
    hero_cta_secondary = cat.get("hero_cta_secondary", "Qué incluye")
    hero_problem = cat.get("hero_problem") or c.get("hero_problem", "")

    trust_badges = ux.get("trust_badges") or []
    trust_html = ""
    for b in trust_badges:
        trust_html += f"""<div class="trust-badge">
          <span class="trust-icon" aria-hidden="true">{escape(b.get('icon','•')[:4])}</span>
          <strong>{escape(b.get('label',''))}</strong>
          <span>{escape(b.get('hint',''))}</span>
        </div>"""

    role_chips = '<button type="button" class="role-chip is-active" data-rol="todos">Todos los roles</button>'
    for r in roles:
        role_chips += f'<button type="button" class="role-chip" data-rol="{escape(r.get("slug",""))}">{escape(r.get("nombre",""))}</button>'

    book_chips = '<button type="button" class="book-chip is-active" data-libro="todos">Todos los libros</button>'
    for s in serie:
        chip_label = s.get("titulo_corto") or s.get("titulo", "") or s.get("slug", "")
        book_chips += f'<button type="button" class="book-chip" data-libro="{escape(s.get("slug",""))}">{escape(chip_label)}</button>'

    role_names = {r.get("slug", ""): r.get("nombre", "") for r in roles}
    guias_disponibles = ""
    guias_proximamente = ""
    for g in catalogo:
        gsrc = _guia_src(a, g, portada)
        rol = g.get("rol", "")
        libro = g.get("libro", "")
        rol_label = role_names.get(rol, rol.replace("-", " ").title())
        dis = g.get("disponible", True)
        opacity = "" if dis else ' style="opacity:0.55"'
        btn = '<a class="btn btn-block" href="#">Comprar PDF</a>' if dis else '<span class="btn btn-outline btn-block" style="line-height:46px">Avísame</span>'
        badge = ""
        img = f'<img class="card-img" src="{escape(gsrc)}" alt="{escape(g.get("titulo",""))}"/>' if dis else '<div class="card-soon">Próximamente</div>'
        brand_label = f"{escape(name)} · PDF" if dis else escape(name)
        card = f"""
      <article class="card guia-card" data-rol-card="{escape(rol)}" data-libro-card="{escape(libro)}"{opacity}>
        {badge}
        {img}
        <div class="card-body">
          <p class="card-brand">{brand_label}</p>
          <h3>{escape(g.get("titulo","") if dis else "Nueva guía en camino")}</h3>
          <p class="price">{escape(g.get("precio", precio_display) if dis else "—")}</p>
          {btn}
        </div>
      </article>"""
        if dis:
            guias_disponibles += card
        else:
            guias_proximamente += card

    soon_count = sum(1 for g in catalogo if not g.get("disponible", True))
    soon_block = ""
    if guias_proximamente:
        soon_block = f"""<details class="soon-section">
      <summary>Próximamente · {soon_count} guía{"s" if soon_count != 1 else ""}</summary>
      <div class="grid">{guias_proximamente}</div>
    </details>"""

    incluye = ux.get("incluye_semanas") or []
    incluye_html = "".join(f"<li>{escape(x)}</li>" for x in incluye[:6])

    faq_items = ux.get("faq") or []
    faq_html = ""
    for i, item in enumerate(faq_items):
        faq_html += f"""<details class="faq-item">
          <summary>{escape(item.get('q',''))}</summary>
          <p>{escape(item.get('a',''))}</p>
        </details>"""

    roles_map = {
        r.get("slug", ""): {"nombre": r.get("nombre", ""), "ejemplo": r.get("ejemplo", "")}
        for r in roles
    }
    roles_json = json.dumps(roles_map, ensure_ascii=False).replace("</", "<\\/")

    lifestyle_html = ""
    if imagen_lectura and ux.get("show_lifestyle", True):
        cap = cat.get("lifestyle_caption", "")
        cap_html = f"<figcaption>{escape(cap)}</figcaption>" if cap else ""
        lifestyle_html = f"""<figure class="hero-lifestyle">
      <img src="{escape(imagen_lectura)}" alt="Profesional leyendo guía PDF"/>
      {cap_html}
    </figure>"""

    soon_placeholder = f"""
      <article class="card guia-card card-placeholder" data-rol-card="todos" data-libro-card="todos">
        <div class="card-soon">Próximamente</div>
        <div class="card-body">
          <p class="card-brand">{escape(name)}</p>
          <h3>Nueva guía en camino</h3>
          <p class="price">—</p>
          <span class="btn btn-card btn-block" style="line-height:42px">Avísame</span>
        </div>
      </article>"""

    def _card_for_guia(g: dict) -> str:
        gsrc = _guia_src(a, g, portada)
        rol = g.get("rol", "")
        libro = g.get("libro", "")
        dis = g.get("disponible", True)
        opacity = "" if dis else ' style="opacity:0.72"'
        btn = (
            '<a class="btn btn-card btn-block" href="#">Comprar PDF</a>'
            if dis
            else '<span class="btn btn-card btn-outline btn-block" style="line-height:42px">Avísame</span>'
        )
        libro_slug = g.get("libro", "")
        libro_src = a.get(f"libro_{libro_slug}", "")
        if dis:
            img = f'<img class="card-img" src="{escape(gsrc)}" alt="{escape(g.get("titulo",""))}"/>'
        elif libro_src:
            img = f'<img class="card-img card-img-soon" src="{escape(libro_src)}" alt="{escape(g.get("titulo",""))}"/>'
        else:
            img = f'<div class="card-soon">{escape(g.get("titulo_corto") or "Próximamente")}</div>'
        brand_label = f"{escape(name)} · PDF" if dis else escape(name)
        return f"""
      <article class="card guia-card" data-rol-card="{escape(rol)}" data-libro-card="{escape(libro)}"{opacity}>
        {img}
        <div class="card-body">
          <p class="card-brand">{brand_label}</p>
          <h3>{escape(g.get("titulo",""))}</h3>
          <p class="price">{escape(g.get("precio", precio_display) if dis else "Próximamente")}</p>
          {btn}
        </div>
      </article>"""

    bestseller_pool = catalogo[:4] if catalogo else []
    mas_vendidas_html = "".join(_card_for_guia(g) for g in bestseller_pool)
    for _ in range(max(0, 4 - len(bestseller_pool))):
        mas_vendidas_html += soon_placeholder

    reviews = [
        ("María", "«Me ayudó a priorizar casos en el gabinete.»"),
        ("Carolina", "«Descarga al instante y plan de 10 semanas claro.»"),
        ("Andrea", "«Resumen adaptado a psicopedagogas, no genérico.»"),
        ("Lucía", "«Por fin un PDF que habla mi idioma profesional.»"),
    ]
    reviews_html = "".join(
        f'<blockquote class="review"><p>{escape(q)}</p><cite>— {escape(n)}</cite></blockquote>'
        for n, q in reviews
    )
    about_tagline = cat.get("about_tagline") or m.get("producto_piloto", {}).get("subtitulo", "")

    hero_banner = ""
    hero_img = a.get("hero_lifestyle") or a.get("imagen_lectura", "")
    if hero_img:
        hero_banner = f"""<figure class="hero-banner">
      <img src="{escape(hero_img)}" alt="Profesional aplicando guía PDF en su trabajo"/>
    </figure>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>{escape(m.get('marca', 'Vértice Pro'))}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --bg:{col.get('bg','#fbfaf8')}; --surface:{col.get('surface','#fff')};
      --text:{col.get('text','#34302c')}; --muted:{col.get('muted','#9a948c')};
      --charcoal:{col.get('charcoal','#3a3632')};
      --accent:{col.get('accent','#a69b8f')}; --accent-soft:{col.get('accent_soft','#ebe8e4')};
      --accent-tint:{col.get('accent_tint','#f6f4f1')}; --sage:{col.get('sage','#9c9890')};
      --sage-tint:{col.get('sage_tint','#f4f3f1')}; --blush:{col.get('blush','#f9f7f5')};
      --border:{col.get('border','#ece9e4')}; --cream:{col.get('cream_dark','#f2efeb')};
      --max:1200px; --pad:clamp(16px,4vw,32px);
    }}
    *,*::before,*::after {{ box-sizing:border-box; margin:0; }}
    html {{ -webkit-text-size-adjust:100%; }}
    body {{
      font-family:'DM Sans',system-ui,sans-serif; color:var(--text); line-height:1.55; overflow-x:hidden;
      background:var(--bg);
    }}
    img {{ max-width:100%; height:auto; display:block; }}
    a {{ color:inherit; text-decoration:none; }}
    .wrap {{ width:100%; max-width:var(--max); margin:0 auto; padding-left:var(--pad); padding-right:var(--pad); }}

    .ticker {{ overflow:hidden; background:var(--bg); border-bottom:1px solid var(--border); padding:10px 0; }}
    .ticker-track {{
      display:flex; width:max-content; gap:3rem; animation:marquee 28s linear infinite;
      font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted);
    }}
    .ticker-track span {{ white-space:nowrap; padding-right:3rem; }}
    .ticker-star {{ color:var(--accent); }}
    @keyframes marquee {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}

    header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:22px var(--pad) 18px; position:sticky; top:0; z-index:50; }}
    header .wrap {{ display:flex; flex-direction:column; align-items:center; gap:16px; }}
    .logo {{
      font-family:'Cormorant Garamond',Georgia,serif; font-size:clamp(1.2rem,3.5vw,1.55rem);
      letter-spacing:0.24em; font-weight:500; color:var(--charcoal); line-height:1.2;
    }}
    nav {{ display:flex; flex-wrap:wrap; justify-content:center; gap:clamp(18px,3.5vw,32px); font-size:0.7rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); }}
    nav a {{ padding:4px 0; min-height:40px; display:inline-flex; align-items:center; transition:color 0.2s ease; }}
    nav a:hover {{ color:var(--charcoal); }}

    .hero-editorial {{ padding:0 0 clamp(48px,8vw,72px); background:var(--surface); }}
    .hero-banner {{
      width:100%; max-height:clamp(180px,28vw,320px); overflow:hidden; margin-bottom:clamp(24px,4vw,36px);
      border-bottom:1px solid var(--border);
    }}
    .hero-banner img {{ width:100%; height:clamp(180px,28vw,320px); object-fit:cover; object-position:center 30%; display:block; }}
    .hero-visual {{ display:flex; flex-direction:column; align-items:center; gap:12px; margin-bottom:clamp(28px,5vw,40px); }}
    .hero-showcase {{
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      width:min(100%,520px); margin:0 auto;
    }}
    .hero-showcase .hero-carousel {{
      position:relative; width:min(100%,420px); height:clamp(300px,42vw,460px);
      perspective:900px; touch-action:pan-y; user-select:none;
    }}
    .carousel-track {{ position:relative; width:100%; height:100%; }}
    .carousel-slide {{
      position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
      opacity:0; transform:translateX(20px) scale(0.94);
      transition:opacity 0.5s ease, transform 0.5s ease; pointer-events:none;
    }}
    .carousel-slide.is-active {{ opacity:1; transform:translateX(0) scale(1); pointer-events:auto; }}
    .carousel-slide.is-soon img {{ opacity:0.7; }}
    .carousel-slide img {{
      width:min(68%,280px); max-height:100%; object-fit:contain;
      filter:drop-shadow(0 16px 40px rgba(52,48,44,0.06));
    }}
    .carousel-nav {{ display:flex; align-items:center; justify-content:center; gap:10px; }}
    .carousel-btn {{
      width:40px; height:40px; border:1px solid var(--border); background:var(--surface);
      border-radius:50%; cursor:pointer; font-size:1rem; line-height:1; color:var(--muted);
      display:inline-flex; align-items:center; justify-content:center;
    }}
    .carousel-btn:hover {{ border-color:var(--charcoal); color:var(--charcoal); }}
    .carousel-dots {{ display:flex; gap:7px; }}
    .carousel-dot {{
      width:6px; height:6px; border-radius:50%; border:none; padding:0; background:var(--border); cursor:pointer;
    }}
    .carousel-dot.is-active {{ background:var(--charcoal); }}
    .carousel-caption {{ display:none; }}

    .hero-copy {{ max-width:560px; margin:0 auto; text-align:center; padding:0 var(--pad); }}
    .hero-series {{
      font-size:0.62rem; letter-spacing:0.18em; text-transform:uppercase;
      color:var(--muted); margin-bottom:16px;
    }}
    .hero h1 {{
      font-family:'Cormorant Garamond',serif; font-size:clamp(2.1rem,5.5vw,3rem); font-weight:400;
      line-height:1.12; margin-bottom:16px; letter-spacing:0.01em; color:var(--charcoal);
    }}
    .hero-desc {{ color:var(--muted); font-size:0.94rem; margin-bottom:26px; max-width:42ch; margin-left:auto; margin-right:auto; line-height:1.65; }}
    .hero-actions {{ display:flex; justify-content:center; }}

    #guias-por-rol {{ background:var(--bg); }}
    .grid-mas-vendidas {{
      display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:clamp(14px,2.5vw,24px);
      max-width:var(--max); margin:0 auto; padding:0 var(--pad);
    }}
    .section-foot {{ text-align:center; margin-top:clamp(24px,4vw,36px); }}
    .section-foot a {{
      font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted);
      border-bottom:1px solid var(--border); padding-bottom:2px; transition:color 0.2s ease, border-color 0.2s ease;
    }}
    .section-foot a:hover {{ color:var(--charcoal); border-color:var(--charcoal); }}

    .about {{ background:var(--accent-tint); }}
    .about .wrap {{ max-width:680px; text-align:center; }}
    .about h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.6rem,4vw,2.15rem); font-weight:400; margin-bottom:20px; letter-spacing:0.02em; color:var(--charcoal); }}
    .about p {{ color:var(--muted); font-size:0.92rem; line-height:1.7; margin-bottom:14px; }}
    .about-tagline {{ color:var(--text); font-size:0.92rem; margin:20px 0 28px; font-style:italic; }}

    section {{ padding:clamp(56px,10vw,96px) var(--pad); }}
    section h2 {{
      font-family:'Cormorant Garamond',serif; font-size:clamp(1.35rem,3.5vw,1.75rem); font-weight:400;
      text-align:center; letter-spacing:0.06em; text-transform:uppercase; color:var(--charcoal);
      margin-bottom:clamp(28px,5vw,44px);
    }}

    .btn {{
      display:inline-flex; align-items:center; justify-content:center; min-height:46px; min-width:168px; padding:0 28px;
      background:var(--charcoal); color:#fff; font-size:0.72rem; font-weight:500; letter-spacing:0.12em; text-transform:uppercase;
      border:1px solid var(--charcoal); cursor:pointer; transition:opacity 0.2s ease;
    }}
    .btn:hover {{ opacity:0.88; }}
    .btn-outline {{ background:transparent; color:var(--charcoal); border-color:var(--border); }}
    .btn-outline:hover {{ border-color:var(--charcoal); opacity:1; }}
    .btn-card {{
      min-height:42px; min-width:0; width:100%; padding:0 12px; font-size:0.68rem;
      background:transparent; color:var(--charcoal); border:1px solid var(--charcoal);
    }}
    .btn-card:hover {{ background:var(--charcoal); color:#fff; opacity:1; }}
    .btn-block {{ width:100%; }}

    .card {{ background:transparent; border:none; display:flex; flex-direction:column; }}
    .card-img {{ aspect-ratio:1; object-fit:cover; background:var(--accent-tint); padding:0; width:100%; border-radius:2px; }}
    .card-img-soon {{ opacity:0.82; filter:saturate(0.85); }}
    .card-body {{ padding:14px 2px 0; text-align:center; flex:1; display:flex; flex-direction:column; gap:4px; }}
    .card-brand {{ font-size:0.58rem; letter-spacing:0.14em; color:var(--muted); text-transform:uppercase; margin-bottom:4px; }}
    .card h3 {{
      font-family:'Cormorant Garamond',serif; font-size:1rem; font-weight:500; line-height:1.35;
      margin-bottom:6px; flex:1; color:var(--charcoal);
    }}
    .price {{ font-size:0.95rem; font-weight:500; margin-bottom:12px; color:var(--text); }}
    .card-soon {{
      aspect-ratio:1; background:var(--sage-tint); display:flex; align-items:center; justify-content:center;
      color:var(--muted); font-size:0.78rem; letter-spacing:0.06em; text-transform:uppercase; border-radius:2px;
    }}

    #opiniones {{ background:var(--surface); }}
    .reviews {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:clamp(16px,3vw,28px); max-width:var(--max); margin:0 auto; }}
    .review {{
      background:transparent; border:none; padding:8px 12px; font-size:0.86rem; color:var(--muted); text-align:center;
    }}
    .review p {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:1rem; line-height:1.55; color:var(--text); margin-bottom:10px; }}
    .review cite {{ display:block; font-style:normal; font-size:0.72rem; letter-spacing:0.06em; text-transform:uppercase; color:var(--muted); }}

    .newsletter {{
      background:var(--blush); border-top:1px solid var(--border); padding:clamp(48px,8vw,72px) var(--pad); text-align:center;
    }}
    .newsletter h2 {{
      font-family:'Cormorant Garamond',serif; font-size:clamp(1.35rem,3.5vw,1.75rem); margin-bottom:8px; font-weight:400;
      letter-spacing:0.04em; text-transform:none; color:var(--charcoal);
    }}
    .newsletter p {{ color:var(--muted); font-size:0.88rem; margin-bottom:22px; }}
    .newsletter-form {{ display:flex; flex-wrap:wrap; gap:0; justify-content:center; max-width:420px; margin:0 auto; }}
    .newsletter-form input {{
      flex:1 1 180px; min-height:46px; border:1px solid var(--border); border-right:none; padding:0 14px;
      font:inherit; background:var(--surface);
    }}
    .newsletter-form .btn {{ min-width:132px; border-left:none; }}

    footer {{ padding:28px var(--pad) 36px; text-align:center; font-size:0.7rem; color:var(--muted); line-height:1.65; background:var(--bg); border-top:1px solid var(--border); }}
    footer p + p {{ margin-top:6px; }}

    @media (max-width:960px) {{
      .grid-mas-vendidas {{ grid-template-columns:repeat(2,minmax(0,1fr)); max-width:520px; }}
      .reviews {{ grid-template-columns:repeat(2,minmax(0,1fr)); max-width:520px; }}
    }}
    @media (max-width:768px) {{
      .hero-showcase .hero-carousel {{ width:min(88vw,360px); height:clamp(280px,52vw,380px); }}
      .grid-mas-vendidas {{ max-width:320px; }}
      .reviews {{ grid-template-columns:1fr; max-width:360px; }}
      .newsletter-form {{ flex-direction:column; }}
      .newsletter-form input {{ border-right:1px solid var(--border); }}
      .newsletter-form .btn {{ border-left:1px solid var(--charcoal); width:100%; }}
    }}
  </style>
</head>
<body>
  <div class="ticker">
    <div class="ticker-track" aria-hidden="true">
      <span><span class="ticker-star">★</span> 4.9 · 10% primera compra · Descarga instantánea · Guías PDF en español</span>
      <span><span class="ticker-star">★</span> 4.9 · 10% primera compra · Descarga instantánea · Guías PDF en español</span>
    </div>
  </div>

  <header>
    <div class="wrap">
      <div class="logo">{escape(name)}</div>
      <nav>
        <a href="#guias-por-rol">Guías</a>
        <a href="#nosotros">Nosotros</a>
        <a href="#opiniones">Opiniones</a>
      </nav>
    </div>
  </header>

  <section class="hero hero-editorial">
    {hero_banner}
    <div class="hero-visual wrap">
      <div class="hero-showcase">
        <div class="hero-carousel" id="heroCarousel" data-slides="{escape(carousel_json)}">
          <div class="carousel-track">{slides_html}</div>
        </div>
      </div>
      <div class="carousel-nav">
        <button type="button" class="carousel-btn" id="carouselPrev" aria-label="Anterior">‹</button>
        <div class="carousel-dots" id="carouselDots">{dots_html}</div>
        <button type="button" class="carousel-btn" id="carouselNext" aria-label="Siguiente">›</button>
      </div>
    </div>
    <div class="hero-copy">
      <p class="hero-series">{escape(cat.get('hero_series', m.get('serie', 'Aplicar en tu rol')))}</p>
      <h1>{hero_title_html}</h1>
      {f'<p class="hero-desc">{escape(hero_subtitle)}</p>' if hero_subtitle else ''}
      <div class="hero-actions">
        <a class="btn" href="#guias-por-rol">{escape(c.get('hero_cta', cat.get('hero_cta','Ver colección')))}</a>
      </div>
    </div>
  </section>
{lifestyle_html}

  <section id="guias-por-rol">
    <h2>{escape(cat.get('guias_title', c.get('guias_title', 'Más vendidas')))}</h2>
    <div class="grid grid-mas-vendidas" id="guiasDisponibles">{mas_vendidas_html}</div>
    <p class="section-foot"><a href="#guias-por-rol">Ver todo</a></p>
  </section>

  <section id="nosotros" class="about">
    <div class="wrap">
      <h2>{escape(cat.get('about_title', 'Inspiradas en tu trabajo real'))}</h2>
      <p>{escape(cat.get('about_text', ''))}</p>
      {f'<p class="about-tagline">{escape(about_tagline)}</p>' if about_tagline else ''}
      <a class="btn btn-outline" href="#guias-por-rol">Ver colección</a>
    </div>
  </section>

  <section id="opiniones">
    <h2>Lo que dicen</h2>
    <div class="reviews">{reviews_html}</div>
  </section>

  <div class="newsletter wrap">
    <h2>10% en tu primera guía</h2>
    <p>Suscríbete y recibe el descuento en tu primer PDF.</p>
    <form class="newsletter-form" action="#" onsubmit="return false;">
      <input type="email" placeholder="Tu email" aria-label="Email"/>
      <button type="submit" class="btn">Suscribirme</button>
    </form>
  </div>
  </div>

  <footer>
    <p>{escape(c.get('footer_legal','Estas guías son resúmenes independientes. No están afiliadas ni respaldadas por los autores ni editoriales de los libros originales.'))}</p>
    <p>© {escape(m.get('marca', 'Vértice Pro'))}</p>
  </footer>
  <script>
(function() {{
  const root = document.getElementById('heroCarousel');
  if (!root) return;
  const slides = root.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  const titleEl = document.getElementById('captionTitle');
  let idx = 0;
  let timer;
  let touchX = 0;

  function show(i) {{
    idx = (i + slides.length) % slides.length;
    slides.forEach((s, n) => s.classList.toggle('is-active', n === idx));
    dots.forEach((d, n) => d.classList.toggle('is-active', n === idx));
    const s = slides[idx];
    if (titleEl) titleEl.textContent = s.dataset.title || '';
  }}

  function next() {{ show(idx + 1); }}
  function prev() {{ show(idx - 1); }}
  function resetTimer() {{
    clearInterval(timer);
    timer = setInterval(next, 5000);
  }}

  document.getElementById('carouselNext')?.addEventListener('click', () => {{ next(); resetTimer(); }});
  document.getElementById('carouselPrev')?.addEventListener('click', () => {{ prev(); resetTimer(); }});
  dots.forEach(d => d.addEventListener('click', () => {{ show(+d.dataset.index); resetTimer(); }}));

  root.addEventListener('touchstart', e => {{ touchX = e.touches[0].clientX; }}, {{passive:true}});
  root.addEventListener('touchend', e => {{
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 40) {{ dx < 0 ? next() : prev(); resetTimer(); }}
  }}, {{passive:true}});

  resetTimer();
}})();
  </script>
</body>
</html>"""


class AssemblerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        out = slug_output(ctx.slug)
        assets_src = out / "assets"
        preview = out / "preview.html"
        preview.write_text(_render_html(ctx), encoding="utf-8")

        theme_bundle = out / "shopify_bundle"
        if theme_bundle.exists():
            shutil.rmtree(theme_bundle)
        theme_bundle.mkdir(parents=True)
        theme_src = shopify_theme_src()
        if theme_src.is_dir():
            shutil.copytree(theme_src, theme_bundle / "theme", dirs_exist_ok=True)
        if assets_src.is_dir():
            for f in assets_src.iterdir():
                if f.is_file() and f.suffix.lower() in {".svg", ".png", ".jpg", ".webp"}:
                    shutil.copy2(f, theme_bundle / "theme" / "assets" / f.name)

        zip_path = out / "vertice-pro-theme.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            theme_dir = theme_bundle / "theme"
            if theme_dir.is_dir():
                for f in theme_dir.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(theme_dir))

        return AgentResult(ok=True, data={"preview": str(preview), "zip": str(zip_path)})

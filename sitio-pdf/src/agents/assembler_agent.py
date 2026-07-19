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

    compare_items = cat.get("compare_items") or []
    compare_html = ""
    for row in compare_items:
        compare_html += f"""<div class="compare-row">
          <span class="compare-us">{escape(row.get('nosotros',''))}</span>
          <span class="compare-vs">vs</span>
          <span class="compare-them">{escape(row.get('ellos',''))}</span>
        </div>"""

    pasos = ux.get("flujo_pasos") or []
    pasos_html = ""
    for i, paso in enumerate(pasos[:3], 1):
        pasos_html += f"""<article class="paso-card">
          <span class="paso-num">{i}</span>
          <h3>{escape(paso.get('titulo',''))}</h3>
          <p>{escape(paso.get('texto',''))}</p>
        </article>"""

    roles_html = ""
    for r in roles[:6]:
        roles_html += f"""<button type="button" class="rol-card" data-rol-target="{escape(r.get('slug',''))}">
          <strong>{escape(r.get('nombre',''))}</strong>
          <span>{escape(r.get('ejemplo',''))}</span>
        </button>"""

    benefits_html = ""
    for b in benefits[:3]:
        benefits_html += f"""<article class="benefit-card">
          <h3>{escape(b.get('title',''))}</h3>
          <p>{escape(b.get('text',''))}</p>
        </article>"""

    piloto = m.get("producto_piloto") or {}
    featured_html = ""
    for g in catalogo:
        if g.get("disponible") and g.get("slug") == piloto.get("slug"):
            gsrc = _guia_src(a, g, portada)
            featured_html = f"""<aside class="featured-box" id="destacada">
        <span class="featured-label">{escape(cat.get('featured_label','Más vendida'))}</span>
        <div class="featured-inner">
          <img src="{escape(gsrc)}" alt="{escape(g.get('titulo',''))}"/>
          <div>
            <h3>{escape(g.get('titulo',''))}</h3>
            <p class="featured-price">{escape(g.get('precio', precio_display))} · PDF al instante</p>
            <p class="featured-guarantee">{escape(cat.get('garantia_titulo','Garantía 7 días'))}</p>
            <a class="btn" href="#">Comprar PDF</a>
          </div>
        </div>
      </aside>"""
            break

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
        btn = '<a class="btn btn-block" href="#">Comprar PDF</a>' if dis else '<span class="btn btn-outline btn-block" style="line-height:46px">Próximamente</span>'
        badge = '<span class="card-badge">Disponible</span>' if dis else ""
        img = f'<img class="card-img" src="{escape(gsrc)}" alt="{escape(g.get("titulo",""))}"/>' if dis else '<div class="card-soon">Próximamente</div>'
        card = f"""
      <article class="card guia-card" data-rol-card="{escape(rol)}" data-libro-card="{escape(libro)}"{opacity}>
        {badge}
        {img}
        <div class="card-body">
          <p class="card-brand">{escape(rol_label)}</p>
          <h3>{escape(g.get("titulo",""))}</h3>
          <p class="price">{escape(g.get("precio", m.get("precio_display", "$4.99")))}</p>
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
    if imagen_lectura:
        cap = cat.get("lifestyle_caption", "")
        cap_html = f"<figcaption>{escape(cap)}</figcaption>" if cap else ""
        lifestyle_html = f"""<figure class="hero-lifestyle">
      <img src="{escape(imagen_lectura)}" alt="Profesional leyendo guía PDF"/>
      {cap_html}
    </figure>"""

    reviews = [
        ("María G.", "Psicopedagogas", "Prioricé sin leer 300 páginas. Plan claro para el gabinete."),
        ("Roberto L.", "Abogados", "Ejemplos de expedientes reales, no teoría de librería."),
        ("Carmen V.", "Enfermeras", "Lo apliqué en el turno. PDF al instante y sin suscripción."),
    ]
    reviews_html = "".join(
        f'<blockquote class="review"><p>«{escape(q)}»</p><cite>— {escape(n)} · {escape(rol)}</cite></blockquote>'
        for n, rol, q in reviews
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>{escape(m.get('marca', 'Vértice Pro'))}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --bg:{col.get('bg','#faf8f5')}; --surface:{col.get('surface','#fff')};
      --text:{col.get('text','#1a1a1a')}; --muted:{col.get('muted','#6b6560')};
      --charcoal:{col.get('charcoal','#1a1a1a')}; --gold:{col.get('gold','#c9a962')};
      --border:{col.get('border','#e8e4df')}; --cream:{col.get('cream_dark','#f0ebe3')};
      --max:1120px; --pad:clamp(16px,4vw,32px);
    }}
    *,*::before,*::after {{ box-sizing:border-box; margin:0; }}
    html {{ -webkit-text-size-adjust:100%; }}
    body {{ font-family:'DM Sans',system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.55; overflow-x:hidden; }}
    img {{ max-width:100%; height:auto; display:block; }}
    a {{ color:inherit; text-decoration:none; }}
    .wrap {{ width:100%; max-width:var(--max); margin:0 auto; padding-left:var(--pad); padding-right:var(--pad); }}

    .ticker {{ background:var(--charcoal); color:#fff; font-size:0.7rem; letter-spacing:0.05em; padding:10px var(--pad); text-align:center; }}
    header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:16px var(--pad); position:sticky; top:0; z-index:50; }}
    header .wrap {{ display:flex; flex-direction:row; align-items:center; justify-content:space-between; gap:16px; }}
    .logo {{
      font-family:'Cormorant Garamond',Georgia,serif; font-size:clamp(1.05rem,3vw,1.35rem);
      letter-spacing:0.2em; font-weight:500; color:var(--charcoal);
      border-bottom:2px solid var(--gold); padding-bottom:4px; line-height:1.2;
    }}
    nav {{ display:flex; flex-wrap:wrap; justify-content:flex-end; gap:clamp(12px,3vw,24px); font-size:0.72rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); }}
    nav a {{ padding:6px 0; min-height:44px; display:inline-flex; align-items:center; }}

    .hero {{ background:var(--cream); border-bottom:1px solid var(--border); }}
    .hero .wrap {{ display:grid; grid-template-columns:1fr 1fr; gap:clamp(32px,5vw,64px); align-items:center; padding-top:clamp(40px,7vw,72px); padding-bottom:clamp(40px,7vw,72px); }}
    .hero-copy {{ max-width:480px; }}
    .hero-problem {{
      font-size:0.92rem; color:var(--muted); margin-bottom:12px; max-width:38ch; line-height:1.5;
      border-left:3px solid var(--gold); padding-left:14px;
    }}
      display:inline-block; font-size:0.65rem; letter-spacing:0.14em; text-transform:uppercase;
      color:var(--charcoal); background:rgba(255,255,255,0.55); border:1px solid var(--border);
      padding:6px 12px; margin-bottom:18px;
    }}
    .hero-label {{ font-size:0.68rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:12px; }}
    .hero h1 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(2rem,5.5vw,3.15rem); font-weight:400; line-height:1.08; margin-bottom:14px; letter-spacing:0.01em; }}
    .hero-accent {{ font-style:italic; color:var(--gold); font-weight:500; }}
    .hero-desc {{ color:var(--muted); font-size:0.92rem; margin-bottom:18px; max-width:42ch; line-height:1.55; }}
    .hero-bullets {{ list-style:none; margin:0 0 24px; padding:0; display:flex; flex-direction:column; gap:8px; }}
    .hero-bullets li {{
      position:relative; padding-left:18px; font-size:0.88rem; color:var(--text); line-height:1.45;
    }}
    .hero-bullets li::before {{
      content:''; position:absolute; left:0; top:0.55em; width:6px; height:6px; border-radius:50%; background:var(--gold);
    }}
    .hero-actions {{ display:flex; flex-wrap:wrap; align-items:center; gap:12px 20px; }}
    .hero-link {{ font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:var(--charcoal); border-bottom:1px solid var(--gold); padding-bottom:2px; }}
    .hero-link:hover {{ color:var(--gold); }}
    .hero-trust {{ font-size:0.78rem; color:var(--muted); margin-top:16px; letter-spacing:0.02em; }}
    .hero-trust strong {{ color:var(--gold); }}
    .hero-visual {{
      display:flex; flex-direction:column; align-items:center; gap:14px;
      padding:0;
    }}
    .hero-visual-label {{ display:none; }}
    .hero-lifestyle {{ position:relative; margin:0; border-bottom:1px solid var(--border); overflow:hidden; }}
    .hero-lifestyle img {{ width:100%; height:clamp(160px,22vw,260px); object-fit:cover; object-position:center 30%; display:block; }}
    .hero-lifestyle figcaption {{ display:none; }}
    .hero-showcase {{
      position:relative; display:grid; place-items:center;
      width:min(100%,420px); min-height:clamp(300px,42vw,440px);
    }}
    .hero-mockup {{
      position:absolute; right:0; bottom:0; width:min(42%,160px);
      filter:drop-shadow(0 16px 32px rgba(0,0,0,0.12)); z-index:1;
    }}
    .hero-showcase .hero-carousel {{
      position:relative; z-index:2; width:min(72%,300px); height:clamp(260px,36vw,380px);
      perspective:900px; touch-action:pan-y; user-select:none;
    }}
    .carousel-track {{ position:relative; width:100%; height:100%; }}
    .carousel-slide {{
      position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
      opacity:0; transform:translateX(24px) scale(0.92) rotateY(-8deg);
      transition:opacity 0.55s ease, transform 0.55s ease; pointer-events:none;
    }}
    .carousel-slide.is-active {{
      opacity:1; transform:translateX(0) scale(1) rotateY(0); pointer-events:auto;
      animation:floatBook 4s ease-in-out infinite;
    }}
    .carousel-slide.is-soon img {{ opacity:0.88; }}
    .carousel-slide img {{
      width:min(78%,280px); max-height:100%; object-fit:contain;
      filter:drop-shadow(0 24px 48px rgba(0,0,0,0.14));
    }}
    @keyframes floatBook {{
      0%,100% {{ transform:translateY(0) scale(1) rotateY(0); }}
      50% {{ transform:translateY(-10px) scale(1.02) rotateY(2deg); }}
    }}
    .carousel-nav {{ display:flex; align-items:center; justify-content:center; gap:12px; }}
    .carousel-btn {{
      width:44px; height:44px; border:1px solid var(--border); background:var(--surface);
      border-radius:50%; cursor:pointer; font-size:1.1rem; line-height:1; color:var(--charcoal);
      display:inline-flex; align-items:center; justify-content:center;
    }}
    .carousel-btn:hover {{ border-color:var(--gold); }}
    .carousel-dots {{ display:flex; gap:8px; }}
    .carousel-dot {{
      width:8px; height:8px; border-radius:50%; border:none; padding:0; background:var(--border); cursor:pointer;
    }}
    .carousel-dot.is-active {{ background:var(--gold); transform:scale(1.15); }}
    .carousel-caption {{ text-align:center; min-height:2.4em; }}
    .carousel-caption strong {{ display:block; font-family:'Cormorant Garamond',serif; font-size:1.05rem; font-weight:500; color:var(--text); margin-bottom:4px; }}
    .carousel-caption span {{ font-size:0.85rem; color:var(--muted); }}
    .carousel-cta {{ margin-top:10px; font-size:0.72rem; letter-spacing:0.06em; text-transform:uppercase; color:var(--charcoal); border-bottom:1px solid var(--gold); cursor:pointer; background:none; border-top:none; border-left:none; border-right:none; padding:0 0 2px; }}
    .carousel-cta:hover {{ color:var(--gold); }}

    .compare {{
      background:var(--surface); border-bottom:1px solid var(--border);
      padding:clamp(28px,5vw,40px) var(--pad);
    }}
    .compare .wrap {{ text-align:center; }}
    .compare h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.25rem,3.5vw,1.65rem); font-weight:400; margin-bottom:8px; }}
    .compare-lead {{ color:var(--muted); font-size:0.88rem; margin-bottom:20px; }}
    .compare-grid {{ display:grid; gap:10px; max-width:640px; margin:0 auto; }}
    .compare-row {{
      display:grid; grid-template-columns:1fr auto 1fr; gap:12px; align-items:center;
      padding:12px 14px; background:var(--bg); border:1px solid var(--border); font-size:0.82rem;
    }}
    .compare-us {{ text-align:right; font-weight:500; color:var(--charcoal); }}
    .compare-vs {{ font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--gold); }}
    .compare-them {{ text-align:left; color:var(--muted); }}

    .pasos {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr)); gap:20px; max-width:var(--max); margin:0 auto; }}
    .paso-card {{
      background:var(--surface); border:1px solid var(--border); padding:20px; text-align:center;
    }}
    .paso-num {{
      display:inline-flex; width:28px; height:28px; align-items:center; justify-content:center;
      border:1px solid var(--gold); color:var(--gold); font-size:0.75rem; margin-bottom:12px;
    }}
    .paso-card h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.05rem; font-weight:500; margin-bottom:8px; }}
    .paso-card p {{ font-size:0.82rem; color:var(--muted); }}

    .roles-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,220px),1fr)); gap:14px; max-width:var(--max); margin:0 auto; }}
    .rol-card {{
      text-align:left; background:var(--surface); border:1px solid var(--border); padding:16px;
      cursor:pointer; transition:border-color 0.2s, transform 0.2s;
    }}
    .rol-card:hover {{ border-color:var(--gold); transform:translateY(-2px); }}
    .rol-card strong {{ display:block; font-size:0.78rem; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:8px; }}
    .rol-card span {{ font-size:0.82rem; color:var(--muted); line-height:1.45; }}

    .preview-box {{
      display:grid; grid-template-columns:1fr 1fr; gap:clamp(24px,4vw,40px); align-items:center;
      max-width:var(--max); margin:0 auto; background:var(--surface); border:1px solid var(--border);
      padding:clamp(20px,4vw,32px);
    }}
    .preview-box img {{ max-width:220px; margin:0 auto; filter:drop-shadow(0 20px 40px rgba(0,0,0,0.1)); }}
    .preview-copy h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.2rem; margin-bottom:10px; font-weight:500; }}
    .preview-copy p {{ font-size:0.88rem; color:var(--muted); margin-bottom:16px; }}
    .preview-list {{ list-style:none; padding:0; margin:0; }}
    .preview-list li {{ font-size:0.84rem; padding:6px 0 6px 16px; position:relative; color:var(--text); }}
    .preview-list li::before {{ content:'✓'; position:absolute; left:0; color:var(--gold); font-size:0.75rem; }}

    .benefits-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr)); gap:16px; max-width:var(--max); margin:0 auto 28px; }}
    .benefit-card {{ background:var(--surface); border:1px solid var(--border); padding:20px; text-align:center; }}
    .benefit-card h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.05rem; font-weight:500; margin-bottom:8px; }}
    .benefit-card p {{ font-size:0.82rem; color:var(--muted); }}

    .featured-box {{
      max-width:var(--max); margin:0 auto 28px; padding:0 var(--pad);
    }}
    .featured-inner {{
      display:grid; grid-template-columns:auto 1fr; gap:20px; align-items:center;
      background:var(--cream); border:1px solid var(--border); padding:20px;
    }}
    .featured-inner img {{ width:100px; aspect-ratio:3/4; object-fit:contain; background:var(--surface); padding:8px; }}
    .featured-label {{
      display:inline-block; font-size:0.62rem; letter-spacing:0.1em; text-transform:uppercase;
      background:var(--charcoal); color:#fff; padding:4px 10px; margin-bottom:10px;
    }}
    .featured-inner h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.15rem; margin-bottom:8px; font-weight:500; }}
    .featured-price {{ font-size:0.9rem; font-weight:600; margin-bottom:6px; }}
    .featured-guarantee {{ font-size:0.78rem; color:var(--muted); margin-bottom:14px; }}

    .garantia-box {{
      max-width:560px; margin:0 auto 32px; text-align:center;
      background:var(--cream); border:1px solid var(--border); padding:24px 20px;
    }}
    .garantia-box h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.15rem; margin-bottom:8px; font-weight:500; }}
    .garantia-box p {{ font-size:0.86rem; color:var(--muted); }}

    .trust-badges {{
      display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr));
      gap:12px; max-width:var(--max); margin:0 auto; padding:20px var(--pad);
      background:var(--surface); border-bottom:1px solid var(--border);
    }}
    .trust-badge {{ text-align:center; padding:12px 8px; border:1px solid var(--border); background:var(--bg); }}
    .trust-badge strong {{ display:block; font-size:0.72rem; letter-spacing:0.04em; margin-bottom:4px; }}
    .trust-badge span {{ font-size:0.68rem; color:var(--muted); }}
    .trust-icon {{ display:block; font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--gold); margin-bottom:6px; }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; min-width:160px; padding:0 28px; background:var(--charcoal); color:#fff; font-size:0.75rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; border:1px solid var(--charcoal); cursor:pointer; }}
    .btn-outline {{ background:transparent; color:var(--charcoal); }}
    .btn-block {{ width:100%; }}

    section {{ padding:clamp(40px,8vw,64px) var(--pad); }}
    section h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.4rem,4vw,1.85rem); font-weight:400; text-align:center; letter-spacing:0.04em; margin-bottom:clamp(24px,5vw,36px); }}

    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr)); gap:24px; max-width:var(--max); margin:0 auto; }}
    .card {{ background:var(--surface); border:1px solid var(--border); display:flex; flex-direction:column; transition:transform 0.2s ease, box-shadow 0.2s ease; position:relative; }}
    .card:hover {{ transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,0.06); }}
    .card-badge {{
      position:absolute; top:12px; left:12px; z-index:2; background:var(--charcoal); color:#fff;
      font-size:0.58rem; letter-spacing:0.08em; text-transform:uppercase; padding:4px 8px;
    }}
    .card-img {{ aspect-ratio:3/4; object-fit:contain; background:var(--cream); padding:16px; width:100%; }}
    .card-body {{ padding:20px; text-align:center; flex:1; display:flex; flex-direction:column; }}
    .card-brand {{ font-size:0.62rem; letter-spacing:0.12em; color:var(--muted); text-transform:uppercase; margin-bottom:8px; }}
    .card h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.1rem; font-weight:500; line-height:1.35; margin-bottom:10px; flex:1; }}
    .price {{ font-size:1.05rem; font-weight:600; margin-bottom:16px; }}
    .card-soon {{ aspect-ratio:3/4; background:var(--cream); display:flex; align-items:center; justify-content:center; color:var(--muted); font-size:0.85rem; }}

    .role-filters, .book-filters, .filters-row {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px; max-width:var(--max); margin:0 auto 12px; padding:0 var(--pad); }}
    .book-filters, .filters-row.book-filters {{ margin-bottom:24px; }}
    .role-chip, .book-chip {{
      padding:10px 18px; border:1px solid var(--border); background:var(--surface);
      font-size:0.72rem; letter-spacing:0.06em; text-transform:uppercase; cursor:pointer;
      color:var(--muted); border-radius:999px;
    }}
    .role-chip.is-active, .book-chip.is-active {{ background:var(--charcoal); color:#fff; border-color:var(--charcoal); }}
    .filters-row {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px; max-width:var(--max); margin:0 auto 12px; padding:0 var(--pad); }}
    .filters-row.book-filters {{ margin-bottom:24px; }}
    .guia-card[hidden] {{ display:none !important; }}
    .empty-state {{ text-align:center; color:var(--muted); font-size:0.9rem; padding:24px; grid-column:1/-1; display:none; }}
    .empty-state.is-visible {{ display:block; }}
    .soon-section {{ max-width:var(--max); margin:32px auto 0; padding:0 var(--pad); }}
    .soon-section summary {{
      cursor:pointer; text-align:center; font-size:0.78rem; letter-spacing:0.08em;
      text-transform:uppercase; color:var(--muted); padding:12px; list-style:none;
    }}
    .soon-section summary::-webkit-details-marker {{ display:none; }}
    .soon-section[open] summary {{ margin-bottom:20px; color:var(--text); }}
    .section-lead {{ text-align:center; color:var(--muted); font-size:0.9rem; max-width:40ch; margin:-12px auto 24px; padding:0 var(--pad); }}

    .incluye-box {{
      max-width:640px; margin:0 auto; background:var(--surface); border:1px solid var(--border);
      padding:clamp(20px,4vw,32px); text-align:left;
    }}
    .incluye-box h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.15rem; margin-bottom:12px; font-weight:500; }}
    .incluye-intro {{ font-size:0.88rem; color:var(--muted); margin-bottom:12px; }}
    .incluye-ejemplo {{
      font-size:0.9rem; color:var(--text); background:var(--cream); border-left:3px solid var(--gold);
      padding:12px 14px; margin-bottom:16px;
    }}
    .incluye-ejemplo[hidden] {{ display:none !important; }}
    .incluye-box ul {{ margin:0; padding-left:1.2em; color:var(--muted); font-size:0.88rem; }}
    .incluye-box li {{ margin-bottom:8px; }}

    .faq {{ max-width:720px; margin:0 auto; }}
    .faq-item {{ border:1px solid var(--border); background:var(--surface); margin-bottom:10px; }}
    .faq-item summary {{ cursor:pointer; padding:16px 18px; font-size:0.9rem; font-weight:500; list-style:none; }}
    .faq-item summary::-webkit-details-marker {{ display:none; }}
    .faq-item p {{ padding:0 18px 16px; font-size:0.86rem; color:var(--muted); }}

    .sticky-cta {{
      position:fixed; bottom:0; left:0; right:0; z-index:60; background:var(--surface);
      border-top:1px solid var(--border); padding:10px var(--pad); display:none;
      transform:translateY(100%); transition:transform 0.25s ease;
      box-shadow:0 -8px 24px rgba(0,0,0,0.06);
    }}
    .sticky-cta.is-visible {{ display:block; transform:translateY(0); }}
    .sticky-cta .wrap {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:0; }}
    .sticky-cta p {{ font-size:0.78rem; color:var(--muted); margin:0; }}
    .sticky-cta .btn {{ min-width:auto; padding:0 18px; min-height:44px; }}

    .newsletter-form {{ display:flex; flex-wrap:wrap; gap:10px; justify-content:center; max-width:420px; margin:0 auto; }}
    .newsletter-form input {{
      flex:1 1 200px; min-height:48px; border:1px solid var(--border); padding:0 14px;
      font:inherit; background:var(--surface);
    }}
    .newsletter-micro {{ font-size:0.72rem; color:var(--muted); margin-top:12px; }}

    .reviews {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr)); gap:20px; max-width:var(--max); margin:0 auto; }}
    .review {{ background:var(--surface); border:1px solid var(--border); padding:20px; font-size:0.86rem; color:var(--muted); }}
    .review cite {{ display:block; margin-top:10px; font-style:normal; font-size:0.72rem; color:var(--text); }}

    .newsletter {{ background:var(--cream); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:clamp(36px,6vw,56px) var(--pad); text-align:center; }}
    .newsletter h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.3rem,4vw,1.75rem); margin-bottom:8px; }}
    .newsletter p {{ color:var(--muted); font-size:0.9rem; margin-bottom:20px; }}

    footer {{ padding:28px var(--pad); text-align:center; font-size:0.7rem; color:var(--muted); line-height:1.5; }}

    @media (max-width:768px) {{
      header .wrap {{ flex-direction:column; align-items:center; }}
      nav {{ justify-content:center; }}
      .hero .wrap {{ grid-template-columns:1fr; text-align:center; }}
      .hero-copy {{ max-width:none; margin:0 auto; }}
      .hero-desc {{ margin-left:auto; margin-right:auto; }}
      .hero-bullets {{ align-items:center; }}
      .hero-bullets li {{ text-align:left; max-width:28ch; }}
      .hero-actions {{ justify-content:center; }}
      .hero-visual {{ order:-1; width:100%; max-width:min(92vw,400px); margin:0 auto; }}
      .hero-showcase .hero-carousel {{ width:min(78vw,300px); height:clamp(240px,48vw,340px); }}
      .hero-mockup {{ width:min(38%,130px); }}
      .compare-row {{ grid-template-columns:1fr; text-align:center; gap:6px; }}
      .compare-us, .compare-them {{ text-align:center; }}
      .preview-box {{ grid-template-columns:1fr; text-align:center; }}
      .featured-inner {{ grid-template-columns:1fr; text-align:center; justify-items:center; }}
      body {{ padding-bottom:72px; }}
    }}
  </style>
</head>
<body>
  <div class="ticker">★ 4.9 · Descarga instantánea · 10% primera compra</div>

  <header>
    <div class="wrap">
      <div class="logo">{escape(name)}</div>
      <nav>
        <a href="#guias-por-rol">Catálogo</a>
        <a href="#como-funciona">Cómo funciona</a>
        <a href="#incluye">Qué incluye</a>
        <a href="#faq">FAQ</a>
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="wrap">
      <div class="hero-copy">
        <p class="hero-series">{escape(cat.get('hero_series', m.get('serie', 'Aplicar en tu rol')))}</p>
        {f'<p class="hero-problem">{escape(hero_problem)}</p>' if hero_problem else ''}
        <h1>{hero_title_html}</h1>
        {f'<p class="hero-desc">{escape(hero_subtitle)}</p>' if hero_subtitle else ''}
        {f'<ul class="hero-bullets">{hero_bullets_html}</ul>' if hero_bullets_html else ''}
        <div class="hero-actions">
          <a class="btn" href="#guias-por-rol">{escape(c.get('hero_cta', cat.get('hero_cta','Ver guías')))}</a>
          <a class="hero-link" href="#como-funciona">{escape(hero_cta_secondary)}</a>
        </div>
        <p class="hero-trust">{escape(cat.get('hero_trust', c.get('hero_trust', '★ 4.9 · Descarga al instante')))}</p>
      </div>
      <div class="hero-visual">
        <div class="hero-showcase">
          <img class="hero-mockup" src="{escape(mockup)}" alt="Vista previa PDF en móvil" width="160" height="300"/>
          <div class="hero-carousel" id="heroCarousel" data-slides="{escape(carousel_json)}">
            <div class="carousel-track">{slides_html}</div>
          </div>
        </div>
        <div class="carousel-nav">
          <button type="button" class="carousel-btn" id="carouselPrev" aria-label="Anterior">‹</button>
          <div class="carousel-dots" id="carouselDots">{dots_html}</div>
          <button type="button" class="carousel-btn" id="carouselNext" aria-label="Siguiente">›</button>
        </div>
        <div class="carousel-caption" id="carouselCaption">
          <strong id="captionTitle">{escape(str(slides[0].get('titulo','')))}</strong>
          <span id="captionSubtitle">{escape(str(first_sub))}</span>
          <button type="button" class="carousel-cta" id="carouselBookCta">Ver guías de este libro</button>
        </div>
      </div>
    </div>
  </section>
{lifestyle_html}

  <section class="compare" id="compare">
    <div class="wrap">
      <h2>{escape(cat.get('compare_titulo','Compra única, PDF tuyo'))}</h2>
      <p class="compare-lead">{escape(cat.get('compare_lead',''))}</p>
      <div class="compare-grid">{compare_html}</div>
    </div>
  </section>

  <div class="trust-badges">{trust_html}</div>

  <section id="como-funciona">
    <h2>{escape(cat.get('como_funciona_titulo','Cómo funciona'))}</h2>
    <div class="pasos">{pasos_html}</div>
  </section>

  <section id="para-quien">
    <h2>{escape(cat.get('para_quien_titulo','¿Para quién es?'))}</h2>
    <p class="section-lead">{escape(cat.get('para_quien_lead',''))}</p>
    <div class="roles-grid" id="rolesGrid">{roles_html}</div>
  </section>

  <section id="preview">
    <h2>{escape(cat.get('preview_titulo','Así se ve tu guía'))}</h2>
    <p class="section-lead">{escape(cat.get('preview_lead',''))}</p>
    <div class="preview-box">
      <img src="{escape(mockup)}" alt="Mockup guía PDF en móvil"/>
      <div class="preview-copy">
        <h3>Plan de 10 semanas incluido</h3>
        <p>Cada semana una acción concreta adaptada a tu oficio — no solo leer, aplicar.</p>
        <ul class="preview-list">{incluye_html}</ul>
      </div>
    </div>
  </section>

  <section id="guias-por-rol">
    <h2>Catálogo</h2>
    <p class="section-lead">{escape(c.get('guias_lead', cat.get('guias_lead', 'Elige tu profesión.')))}</p>
    {featured_html}
    <div class="filters-row role-filters" id="roleFilters">{role_chips}</div>
    <div class="filters-row book-filters" id="bookFilters">{book_chips}</div>
    <div class="grid" id="guiasDisponibles">{guias_disponibles or '<p class="empty-state is-visible" id="emptyDisponibles">Ninguna guía disponible con estos filtros.</p>'}</div>
    {soon_block}
    <p class="empty-state" id="emptyAll">No hay guías con esta combinación. Prueba otro rol o libro.</p>
  </section>

  <section id="incluye">
    <h2>{escape(c.get('benefits_title', cat.get('benefits_title','Qué incluye cada guía')))}</h2>
    <div class="benefits-grid">{benefits_html}</div>
    <div class="incluye-box">
      <h3 id="incluyePlanTitulo">{escape(cat.get('plan_titulo','Estructura del plan · 10 semanas'))}</h3>
      <p class="incluye-intro" id="incluyeIntro">{escape(cat.get('plan_intro_default','Todas las guías siguen la misma estructura.'))}</p>
      <p class="incluye-ejemplo" id="incluyeEjemplo" hidden></p>
      <ul>{incluye_html}</ul>
    </div>
  </section>

  <section id="opiniones">
    <h2>Lo que dicen</h2>
    <div class="reviews">{reviews_html}</div>
  </section>

  <section id="faq">
    <h2>Preguntas frecuentes</h2>
    <div class="garantia-box">
      <h3>{escape(cat.get('garantia_titulo','Garantía de 7 días'))}</h3>
      <p>{escape(cat.get('garantia_texto',''))}</p>
    </div>
    <div class="faq">{faq_html}</div>
  </section>

  <div class="newsletter wrap">
    <h2>10% en tu primera guía</h2>
    <p>Suscríbete y recibe el descuento en tu primer PDF.</p>
    <form class="newsletter-form" action="#" onsubmit="return false;">
      <input type="email" placeholder="tu@email.com" aria-label="Email"/>
      <button type="submit" class="btn">Quiero el 10%</button>
    </form>
    <p class="newsletter-micro">{escape(ux.get('newsletter_microcopy',''))}</p>
  </div>

  <div class="sticky-cta" id="stickyCta">
    <div class="wrap">
      <p><strong>Desde {escape(precio_display)}</strong> · PDF al instante</p>
      <a class="btn" href="#guias-por-rol">Ver guías</a>
    </div>
  </div>

  <footer><p><strong>{escape(m.get('marca', 'Vértice Pro'))}</strong> · {escape(m.get('tagline', 'Aplicar en tu rol'))} · {escape(m.get('descripcion_corta', ''))}</p><p>{escape(c.get('footer_legal',''))}</p></footer>
  <script>
  const ROLES_DATA = {roles_json};
  const INCLUYE_DEFAULT = {json.dumps(cat.get('plan_intro_default',''), ensure_ascii=False)};
  const INCLUYE_ROL_PREFIX = {json.dumps(cat.get('plan_intro_rol',''), ensure_ascii=False)};
(function() {{
  const root = document.getElementById('heroCarousel');
  if (!root) return;
  const slides = root.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  const titleEl = document.getElementById('captionTitle');
  const priceEl = document.getElementById('captionSubtitle');
  let idx = 0;
  let timer;
  let touchX = 0;

  function show(i) {{
    idx = (i + slides.length) % slides.length;
    slides.forEach((s, n) => s.classList.toggle('is-active', n === idx));
    dots.forEach((d, n) => d.classList.toggle('is-active', n === idx));
    const s = slides[idx];
    if (titleEl) titleEl.textContent = s.dataset.title || '';
    if (priceEl) priceEl.textContent = s.dataset.subtitle || '';
    root.dataset.activeSlug = s.dataset.slug || '';
  }}

  function next() {{ show(idx + 1); }}
  function prev() {{ show(idx - 1); }}
  function resetTimer() {{
    clearInterval(timer);
    timer = setInterval(next, 4500);
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
  if (slides[0]) root.dataset.activeSlug = slides[0].dataset.slug || '';
}})();
(function() {{
  const roleChips = document.querySelectorAll('.role-chip');
  const bookChips = document.querySelectorAll('.book-chip');
  const cards = document.querySelectorAll('.guia-card');
  const emptyAll = document.getElementById('emptyAll');
  let activeRol = 'todos';
  let activeLibro = 'todos';

  function applyFilters() {{
    let visible = 0;
    cards.forEach(card => {{
      const matchRol = activeRol === 'todos' || card.dataset.rolCard === activeRol;
      const matchLibro = activeLibro === 'todos' || card.dataset.libroCard === activeLibro;
      const show = matchRol && matchLibro;
      card.hidden = !show;
      if (show) visible++;
    }});
    if (emptyAll) emptyAll.classList.toggle('is-visible', visible === 0);
    updateIncluye(activeRol);
  }}

  function updateIncluye(rol) {{
    const intro = document.getElementById('incluyeIntro');
    const ej = document.getElementById('incluyeEjemplo');
    if (!intro || !ej) return;
    if (rol === 'todos' || !ROLES_DATA[rol]) {{
      intro.textContent = INCLUYE_DEFAULT;
      ej.hidden = true;
      ej.textContent = '';
      return;
    }}
    const data = ROLES_DATA[rol];
    intro.textContent = INCLUYE_ROL_PREFIX + ' ' + (data.nombre || rol) + '.';
    ej.textContent = data.ejemplo || '';
    ej.hidden = !data.ejemplo;
  }}

  roleChips.forEach(btn => btn.addEventListener('click', () => {{
    activeRol = btn.dataset.rol;
    roleChips.forEach(c => c.classList.toggle('is-active', c === btn));
    applyFilters();
    if (activeRol !== 'todos') {{
      document.getElementById('guiasDisponibles')?.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}
  }}));

  bookChips.forEach(btn => btn.addEventListener('click', () => {{
    activeLibro = btn.dataset.libro;
    bookChips.forEach(c => c.classList.toggle('is-active', c === btn));
    applyFilters();
  }}));

  document.getElementById('carouselBookCta')?.addEventListener('click', () => {{
    const slug = document.getElementById('heroCarousel')?.dataset.activeSlug;
    if (slug) {{
      activeLibro = slug;
      bookChips.forEach(c => c.classList.toggle('is-active', c.dataset.libro === slug));
      applyFilters();
    }}
    document.getElementById('guias-por-rol')?.scrollIntoView({{ behavior: 'smooth' }});
  }});

  document.querySelectorAll('.rol-card').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const rol = btn.dataset.rolTarget;
      if (!rol) return;
      activeRol = rol;
      roleChips.forEach(c => c.classList.toggle('is-active', c.dataset.rol === rol));
      applyFilters();
      document.getElementById('guias-por-rol')?.scrollIntoView({{ behavior: 'smooth' }});
    }});
  }});

  applyFilters();
}})();
(function() {{
  const bar = document.getElementById('stickyCta');
  const hero = document.querySelector('.hero');
  if (!bar || !hero) return;
  const obs = new IntersectionObserver(([e]) => {{
    bar.classList.toggle('is-visible', !e.isIntersecting);
  }}, {{ threshold: 0.1 }});
  obs.observe(hero);
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

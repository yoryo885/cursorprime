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
    slides = data.get("carousel") or ctx.marca.get("catalogo_guias") or []
    if not slides:
        slides = [{"titulo": ctx.marca.get("producto_piloto", {}).get("titulo", "Guía PDF"), "src": ctx.assets.get("portada", ""), "precio": "$4.99", "disponible": True}]
    return slides


def _render_html(ctx: PipelineContext) -> str:
    c = ctx.copy
    m = ctx.marca
    col = m.get("colores", {})
    a = ctx.assets
    p = c.get("product", {})
    name = m.get("marca", "Vértice Pro").upper()
    portada = a.get("portada", "assets/portada-pareto.svg")
    mockup = a.get("mockup_movil", "assets/mockup-movil.svg")
    slides = _carousel_slides(ctx)

    slides_html = ""
    dots_html = ""
    for i, s in enumerate(slides):
        active = " is-active" if i == 0 else ""
        soon = "" if s.get("disponible", True) else " is-soon"
        slides_html += f"""
        <figure class="carousel-slide{active}{soon}" data-index="{i}" data-title="{escape(str(s.get('titulo','')))}" data-price="{escape(str(s.get('precio','')))}">
          <img src="{escape(str(s.get('src', portada)))}" alt="{escape(str(s.get('titulo','')))}" draggable="false"/>
        </figure>"""
        dots_html += f'<button type="button" class="carousel-dot{" is-active" if i == 0 else ""}" data-index="{i}" aria-label="Guía {i+1}"></button>'

    carousel_json = json.dumps(slides, ensure_ascii=False).replace("</", "<\\/")

    reviews = [
        ("María", "Me ayudó a priorizar casos en el gabinete."),
        ("Carolina", "Descarga al instante y plan de 10 semanas claro."),
        ("Andrea", "Resumen adaptado a psicopedagogas, no genérico."),
    ]
    reviews_html = "".join(
        f'<blockquote class="review"><p>«{escape(q)}»</p><cite>— {escape(n)}</cite></blockquote>'
        for n, q in reviews
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
    header .wrap {{ display:flex; flex-direction:column; align-items:center; gap:12px; }}
    .logo {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:clamp(1.15rem,4vw,1.45rem); letter-spacing:0.16em; font-weight:500; }}
    nav {{ display:flex; flex-wrap:wrap; justify-content:center; gap:20px; font-size:0.72rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); }}
    nav a {{ padding:6px 0; min-height:44px; display:inline-flex; align-items:center; }}

    .hero {{ background:var(--cream); border-bottom:1px solid var(--border); }}
    .hero .wrap {{ display:grid; grid-template-columns:1fr 1fr; gap:clamp(24px,5vw,56px); align-items:center; padding-top:clamp(32px,6vw,64px); padding-bottom:clamp(32px,6vw,64px); }}
    .hero-copy {{ max-width:480px; }}
    .hero-label {{ font-size:0.68rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:12px; }}
    .hero h1 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.75rem,5vw,2.75rem); font-weight:400; line-height:1.15; margin-bottom:16px; letter-spacing:0.02em; }}
    .hero-desc {{ color:var(--muted); font-size:0.95rem; margin-bottom:24px; max-width:36ch; }}
    .hero-visual {{ display:flex; flex-direction:column; align-items:center; gap:16px; }}
    .hero-carousel {{ position:relative; width:min(100%,340px); height:clamp(300px,42vw,440px); perspective:900px; touch-action:pan-y; user-select:none; }}
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
    .carousel-caption {{ text-align:center; min-height:3.2em; }}
    .carousel-caption strong {{ display:block; font-family:'Cormorant Garamond',serif; font-size:1.05rem; font-weight:500; color:var(--text); margin-bottom:4px; }}
    .carousel-caption span {{ font-size:0.85rem; color:var(--muted); }}
    .carousel-badge {{ font-size:0.62rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--gold); }}

    .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; min-width:160px; padding:0 28px; background:var(--charcoal); color:#fff; font-size:0.75rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; border:1px solid var(--charcoal); cursor:pointer; }}
    .btn-outline {{ background:transparent; color:var(--charcoal); }}
    .btn-block {{ width:100%; }}

    .trust {{ text-align:center; padding:14px var(--pad); font-size:0.75rem; color:var(--muted); background:var(--surface); border-bottom:1px solid var(--border); }}
    .trust strong {{ color:var(--gold); }}

    section {{ padding:clamp(40px,8vw,64px) var(--pad); }}
    section h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.4rem,4vw,1.85rem); font-weight:400; text-align:center; letter-spacing:0.04em; margin-bottom:clamp(24px,5vw,36px); }}

    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr)); gap:24px; max-width:var(--max); margin:0 auto; }}
    .card {{ background:var(--surface); border:1px solid var(--border); display:flex; flex-direction:column; }}
    .card-img {{ aspect-ratio:3/4; object-fit:contain; background:var(--cream); padding:16px; width:100%; }}
    .card-body {{ padding:20px; text-align:center; flex:1; display:flex; flex-direction:column; }}
    .card-brand {{ font-size:0.62rem; letter-spacing:0.12em; color:var(--muted); text-transform:uppercase; margin-bottom:8px; }}
    .card h3 {{ font-family:'Cormorant Garamond',serif; font-size:1.1rem; font-weight:500; line-height:1.35; margin-bottom:10px; flex:1; }}
    .price {{ font-size:1.05rem; font-weight:600; margin-bottom:16px; }}
    .card-soon {{ aspect-ratio:3/4; background:var(--cream); display:flex; align-items:center; justify-content:center; color:var(--muted); font-size:0.85rem; }}

    .story {{ display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:center; max-width:var(--max); margin:0 auto; background:var(--surface); border:1px solid var(--border); padding:clamp(24px,5vw,48px); }}
    .story img {{ width:min(100%,240px); margin:0 auto; }}
    .story h2 {{ text-align:left; font-size:clamp(1.3rem,3vw,1.75rem); margin-bottom:12px; }}
    .story p {{ color:var(--muted); font-size:0.92rem; margin-bottom:16px; }}

    .reviews {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr)); gap:20px; max-width:var(--max); margin:0 auto; }}
    .review {{ background:var(--surface); border:1px solid var(--border); padding:20px; font-size:0.86rem; color:var(--muted); }}
    .review cite {{ display:block; margin-top:10px; font-style:normal; font-size:0.72rem; color:var(--text); }}

    .newsletter {{ background:var(--cream); border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:clamp(36px,6vw,56px) var(--pad); text-align:center; }}
    .newsletter h2 {{ font-family:'Cormorant Garamond',serif; font-size:clamp(1.3rem,4vw,1.75rem); margin-bottom:8px; }}
    .newsletter p {{ color:var(--muted); font-size:0.9rem; margin-bottom:20px; }}

    footer {{ padding:28px var(--pad); text-align:center; font-size:0.7rem; color:var(--muted); line-height:1.5; }}

    @media (max-width:768px) {{
      .hero .wrap {{ grid-template-columns:1fr; text-align:center; }}
      .hero-copy {{ max-width:none; margin:0 auto; }}
      .hero-desc {{ margin-left:auto; margin-right:auto; }}
      .hero-visual {{ order:-1; width:100%; }}
      .hero-carousel {{ width:min(85vw,320px); height:clamp(280px,55vw,380px); margin:0 auto; }}
      .story {{ grid-template-columns:1fr; text-align:center; }}
      .story h2 {{ text-align:center; }}
      .story img {{ width:min(50vw,200px); }}
    }}
  </style>
</head>
<body>
  <div class="ticker">★★★★★ 4.9 · Descarga instantánea · 10% primera compra</div>

  <header>
    <div class="wrap">
      <div class="logo">{escape(name)}</div>
      <nav>
        <a href="#bestsellers">Guías</a>
        <a href="#historia">Nosotros</a>
        <a href="#opiniones">Opiniones</a>
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="wrap">
      <div class="hero-copy">
        <p class="hero-label">Nuevo · Serie Aplicar en tu rol</p>
        <h1>{escape(c.get('hero_title',''))}</h1>
        <p class="hero-desc">{escape(c.get('hero_subtitle',''))}</p>
        <a class="btn" href="#bestsellers">{escape(c.get('hero_cta','Ver colección'))}</a>
      </div>
      <div class="hero-visual">
        <div class="hero-carousel" id="heroCarousel" data-slides="{escape(carousel_json)}">
          <div class="carousel-track">{slides_html}</div>
        </div>
        <div class="carousel-nav">
          <button type="button" class="carousel-btn" id="carouselPrev" aria-label="Anterior">‹</button>
          <div class="carousel-dots" id="carouselDots">{dots_html}</div>
          <button type="button" class="carousel-btn" id="carouselNext" aria-label="Siguiente">›</button>
        </div>
        <div class="carousel-caption" id="carouselCaption">
          <span class="carousel-badge">Serie Aplicar en tu rol</span>
          <strong id="captionTitle">{escape(str(slides[0].get('titulo','')))}</strong>
          <span id="captionPrice">{escape(str(slides[0].get('precio','')))}</span>
        </div>
      </div>
    </div>
  </section>

  <p class="trust">★★★★★ <strong>4.9</strong> · Guías PDF para profesionales · Descarga al instante</p>

  <section id="bestsellers">
    <h2>Más vendidas</h2>
    <div class="grid">
      <article class="card">
        <img class="card-img" src="{escape(portada)}" alt="{escape(p.get('titulo',''))}"/>
        <div class="card-body">
          <p class="card-brand">Vértice Pro · PDF</p>
          <h3>{escape(p.get('titulo',''))}</h3>
          <p class="price">{escape(p.get('precio',''))}</p>
          <a class="btn btn-block" href="#">Añadir al carrito</a>
        </div>
      </article>
      <article class="card" style="opacity:0.5">
        <div class="card-soon">Próximamente</div>
        <div class="card-body">
          <p class="card-brand">Vértice Pro</p>
          <h3>Nueva guía en camino</h3>
          <p class="price">—</p>
          <span class="btn btn-outline btn-block" style="line-height:46px;">Avísame</span>
        </div>
      </article>
    </div>
  </section>

  <section id="historia">
    <div class="story">
      <img src="{escape(mockup)}" alt="Vista móvil"/>
      <div>
        <h2>Inspiradas en tu trabajo real</h2>
        <p>{escape(c.get('about_text',''))}</p>
        <p>{escape(p.get('subtitulo',''))}</p>
        <a class="btn btn-outline" href="#bestsellers">Ver colección</a>
      </div>
    </div>
  </section>

  <section id="opiniones">
    <h2>Lo que dicen</h2>
    <div class="reviews">{reviews_html}</div>
  </section>

  <div class="newsletter wrap">
    <h2>10% en tu primera guía</h2>
    <p>Suscríbete y recibe el descuento en tu primer PDF.</p>
    <a class="btn" href="#">Suscribirme</a>
  </div>

  <footer><p>{escape(c.get('footer_legal',''))}</p></footer>
  <script>
(function() {{
  const root = document.getElementById('heroCarousel');
  if (!root) return;
  const slides = root.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  const titleEl = document.getElementById('captionTitle');
  const priceEl = document.getElementById('captionPrice');
  let idx = 0;
  let timer;
  let touchX = 0;

  function show(i) {{
    idx = (i + slides.length) % slides.length;
    slides.forEach((s, n) => s.classList.toggle('is-active', n === idx));
    dots.forEach((d, n) => d.classList.toggle('is-active', n === idx));
    const s = slides[idx];
    if (titleEl) titleEl.textContent = s.dataset.title || '';
    if (priceEl) priceEl.textContent = s.dataset.price || '';
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

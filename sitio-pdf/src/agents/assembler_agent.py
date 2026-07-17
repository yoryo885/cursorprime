"""Ensambla preview.html + copia theme Shopify."""

from __future__ import annotations

import shutil
import zipfile
from html import escape
from pathlib import Path

from src.config import shopify_theme_src, slug_output
from src.types import AgentResult, PipelineContext


def _render_html(ctx: PipelineContext) -> str:
    c = ctx.copy
    m = ctx.marca
    colors = m.get("colores", {})
    a = ctx.assets
    p = c.get("product", {})
    benefits = c.get("benefits", [])

    ben_html = ""
    for b in benefits:
        ben_html += f"""
        <div class="benefit">
          <h3>{escape(b.get('title', ''))}</h3>
          <p>{escape(b.get('text', ''))}</p>
        </div>"""

    prod_ben = "".join(f"<li>{escape(x)}</li>" for x in p.get("beneficios", [])[:3])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>{escape(m.get('marca', 'Vértice Pro'))} — Guías PDF</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Libre+Baskerville:wght@700&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --navy:{colors.get('navy','#1e3a5f')}; --accent:{colors.get('accent','#2563eb')};
      --green:{colors.get('green','#059669')}; --bg:{colors.get('bg','#f8f9fb')};
      --surface:{colors.get('surface','#fff')}; --text:{colors.get('text','#1a2332')};
      --muted:{colors.get('muted','#5c6b7a')}; --border:#e2e8f0; --radius:12px;
    }}
    * {{ box-sizing:border-box; margin:0; }}
    body {{ font-family:Inter,system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }}
    .announce {{ background:var(--navy); color:#fff; text-align:center; padding:10px 16px; font-size:0.78rem; }}
    header {{ background:var(--surface); border-bottom:1px solid var(--border); padding:14px 20px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:10; }}
    .logo {{ font-weight:700; font-size:1.15rem; color:var(--navy); }}
    .logo span {{ color:var(--accent); }}
    .hero {{ display:grid; grid-template-columns:1fr 1fr; gap:32px; max-width:1100px; margin:0 auto; padding:40px 20px; align-items:center; }}
    .hero h1 {{ font-family:'Libre Baskerville',Georgia,serif; font-size:clamp(1.6rem,4vw,2.4rem); color:var(--navy); margin-bottom:12px; line-height:1.15; }}
    .hero p {{ color:var(--muted); margin-bottom:20px; font-size:1rem; }}
    .hero-img {{ width:100%; border-radius:var(--radius); box-shadow:0 16px 40px rgba(30,58,95,0.2); }}
    .mockup {{ max-width:220px; margin:0 auto; display:block; }}
    .btn {{ display:inline-flex; align-items:center; min-height:48px; padding:0 28px; background:var(--accent); color:#fff; border-radius:8px; font-weight:600; text-decoration:none; }}
    section {{ max-width:1100px; margin:0 auto; padding:0 20px 48px; }}
    section h2 {{ text-align:center; font-size:1.3rem; color:var(--navy); margin-bottom:24px; }}
    .benefits {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }}
    .benefit {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:24px; }}
    .benefit h3 {{ font-size:0.95rem; margin-bottom:8px; color:var(--navy); }}
    .benefit p {{ font-size:0.85rem; color:var(--muted); }}
    .product-showcase {{ display:grid; grid-template-columns:280px 1fr; gap:32px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:32px; align-items:start; }}
    .portada {{ width:100%; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,0.12); }}
    .badge {{ font-size:0.65rem; font-weight:600; background:rgba(37,99,235,0.1); color:var(--accent); padding:4px 10px; border-radius:4px; display:inline-block; margin-bottom:8px; }}
    .price {{ font-size:1.5rem; font-weight:700; color:var(--green); margin:12px 0; }}
    .product-showcase ul {{ margin:12px 0; padding-left:18px; font-size:0.85rem; color:var(--muted); }}
    .about {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:28px; text-align:center; max-width:640px; margin:0 auto; color:var(--muted); font-size:0.9rem; }}
    footer {{ border-top:1px solid var(--border); padding:28px 20px; text-align:center; font-size:0.75rem; color:var(--muted); margin-top:32px; }}
    @media(max-width:768px) {{
      .hero, .product-showcase, .benefits {{ grid-template-columns:1fr; }}
      .mockup {{ max-width:180px; }}
    }}
  </style>
</head>
<body>
  <div class="announce">{escape(c.get('announce',''))}</div>
  <header>
    <div class="logo">{escape(m.get('marca','V'))}<span>Pro</span></div>
    <a class="btn" href="#guias" style="font-size:0.85rem;padding:0 16px;min-height:40px;">Comprar</a>
  </header>

  <div class="hero">
    <div>
      <h1>{escape(c.get('hero_title',''))}</h1>
      <p>{escape(c.get('hero_subtitle',''))}</p>
      <a class="btn" href="#guias">{escape(c.get('hero_cta',''))}</a>
    </div>
    <div>
      <img class="hero-img" src="{escape(a.get('hero',''))}" alt="Vértice Pro hero"/>
      <img class="mockup" src="{escape(a.get('mockup_movil',''))}" alt="Vista móvil"/>
    </div>
  </div>

  <section id="beneficios">
    <h2>{escape(c.get('benefits_title',''))}</h2>
    <div class="benefits">{ben_html}</div>
  </section>

  <section id="guias">
    <h2>{escape(c.get('products_title',''))}</h2>
    <div class="product-showcase">
      <img class="portada" src="{escape(a.get('portada',''))}" alt="{escape(p.get('titulo',''))}"/>
      <div>
        <span class="badge">PDF · Descarga digital</span>
        <h3 style="font-family:'Libre Baskerville',serif;font-size:1.2rem;color:var(--navy);margin-bottom:8px;">{escape(p.get('titulo',''))}</h3>
        <p style="color:var(--muted);font-size:0.9rem;margin-bottom:8px;">{escape(p.get('subtitulo',''))}</p>
        <p class="price">{escape(p.get('precio',''))}</p>
        <ul>{prod_ben}</ul>
        <a class="btn" href="#">Comprar y descargar</a>
      </div>
    </div>
  </section>

  <section>
    <h2>{escape(c.get('about_title',''))}</h2>
    <div class="about"><p>{escape(c.get('about_text',''))}</p></div>
  </section>

  <footer><p>{escape(c.get('footer_legal',''))}</p></footer>
</body>
</html>"""


class AssemblerAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        out = slug_output(ctx.slug)
        assets_src = out / "assets"
        html = _render_html(ctx)
        preview = out / "preview.html"
        preview.write_text(html, encoding="utf-8")

        # Copiar assets junto al preview
        theme_bundle = out / "shopify_bundle"
        if theme_bundle.exists():
            shutil.rmtree(theme_bundle)
        theme_bundle.mkdir(parents=True)

        theme_src = shopify_theme_src()
        if theme_src.is_dir():
            shutil.copytree(theme_src, theme_bundle / "theme", dirs_exist_ok=True)
        if assets_src.is_dir():
            shutil.copytree(assets_src, theme_bundle / "theme" / "assets" / "generated", dirs_exist_ok=True)

        zip_path = out / "vertice-pro-theme.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            theme_dir = theme_bundle / "theme"
            if theme_dir.is_dir():
                for f in theme_dir.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(theme_dir))
            for f in assets_src.glob("*"):
                if f.is_file():
                    zf.write(f, f"assets/{f.name}")
            zf.write(preview, "preview.html")

        return AgentResult(
            ok=True,
            data={"preview": str(preview), "zip": str(zip_path)},
            warnings=["Importa vertice-pro-theme.zip en Shopify → Temas → Importar"],
        )

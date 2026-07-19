"""SVG decorativos — portadas por guía + carrusel hero."""

from __future__ import annotations

import shutil
from pathlib import Path

from src.config import portada_imagen_path, producto_meta_path, load_json


def _c(marca: dict, key: str, default: str) -> str:
    return marca.get("colores", {}).get(key, default)


def _write(path: Path, svg: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg.strip(), encoding="utf-8")
    return path.name


def portada_svg(marca: dict, titulo: str, *, accent_bar: str | None = None) -> str:
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    gold = accent_bar or _c(marca, "gold", "#c9a962")
    bg = _c(marca, "cream_dark", "#f0ebe3")
    line1 = titulo[:32]
    line2 = titulo[32:64] if len(titulo) > 32 else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 520" role="img">
  <rect width="400" height="520" fill="{bg}"/>
  <rect x="24" y="24" width="352" height="472" fill="#fff" stroke="#e8e4df"/>
  <rect x="24" y="24" width="5" height="472" fill="{gold}"/>
  <text x="48" y="120" fill="{charcoal}" font-family="Georgia,serif" font-size="18" font-weight="700">{line1}</text>
  <text x="48" y="148" fill="{charcoal}" font-family="Georgia,serif" font-size="18" font-weight="700">{line2}</text>
  <text x="48" y="440" fill="{gold}" font-family="system-ui,sans-serif" font-size="10" letter-spacing="0.12em">APLICAR EN TU ROL</text>
  <text x="48" y="462" fill="#6b6560" font-family="system-ui" font-size="9">VÉRTICE PRO · PDF</text>
</svg>"""


def mockup_movil_svg(marca: dict) -> str:
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    bg = _c(marca, "bg", "#faf8f5")
    gold = _c(marca, "gold", "#c9a962")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 520" role="img">
  <rect x="20" y="8" width="240" height="500" rx="28" fill="{charcoal}"/>
  <rect x="32" y="36" width="216" height="444" rx="2" fill="{bg}"/>
  <text x="140" y="64" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="9" letter-spacing="0.14em">VÉRTICE PRO</text>
  <rect x="52" y="88" width="176" height="120" fill="#fff" stroke="#e8e4df"/>
  <rect x="52" y="88" width="4" height="120" fill="{gold}"/>
  <text x="140" y="155" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="9">PDF</text>
  <rect x="52" y="230" width="120" height="5" rx="2" fill="#e8e4df"/>
  <rect x="52" y="248" width="90" height="5" rx="2" fill="#e8e4df"/>
  <rect x="52" y="280" width="176" height="36" fill="{charcoal}"/>
  <text x="140" y="303" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="9">Comprar PDF</text>
</svg>"""


def portada_pareto_pdf_svg(titulo: str, subtitulo: str = "El principio de Pareto · Antoine Delers") -> str:
    """Réplica web de la portada del PDF (fondo negro, 80/20, serie verde)."""
    line1 = titulo[:34]
    line2 = titulo[34:68] if len(titulo) > 34 else ""
    accent = "#4caf7d"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 520" role="img" aria-label="{titulo}">
  <defs>
    <linearGradient id="pg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2d5a45"/>
      <stop offset="100%" stop-color="#0a0a0a"/>
    </linearGradient>
  </defs>
  <rect width="400" height="520" fill="#0a0a0a"/>
  <text x="28" y="44" fill="{accent}" font-family="system-ui,sans-serif" font-size="10" font-weight="600" letter-spacing="0.14em">APLICAR EN TU ROL</text>
  <rect x="0" y="54" width="400" height="188" fill="#141414"/>
  <rect x="0" y="54" width="400" height="188" fill="url(#pg)" opacity="0.75"/>
  <rect x="0" y="54" width="402" height="190" fill="none" stroke="{accent}" stroke-width="2"/>
  <ellipse cx="290" cy="148" rx="90" ry="68" fill="#252525" opacity="0.85"/>
  <ellipse cx="310" cy="132" rx="36" ry="36" fill="#333"/>
  <text x="24" y="300" fill="#ffffff" font-family="system-ui,sans-serif" font-size="76" font-weight="700" letter-spacing="-0.04em">80</text>
  <text x="24" y="368" fill="{accent}" font-family="system-ui,sans-serif" font-size="58" font-weight="700">/20</text>
  <text x="28" y="412" fill="#ffffff" font-family="system-ui,sans-serif" font-size="15" font-weight="700">{line1}</text>
  <text x="28" y="434" fill="#ffffff" font-family="system-ui,sans-serif" font-size="15" font-weight="700">{line2}</text>
  <text x="28" y="468" fill="rgba(255,255,255,0.55)" font-family="system-ui,sans-serif" font-size="10">{subtitulo}</text>
  <text x="28" y="498" fill="rgba(255,255,255,0.4)" font-family="system-ui,sans-serif" font-size="9" letter-spacing="0.08em">VÉRTICE PRO · PDF</text>
</svg>"""


def _portada_for_guia(
    out_dir: Path,
    marca: dict,
    guia: dict,
    *,
    producto: str,
) -> tuple[str, str, bool]:
    """Genera o copia portada. Retorna (filename, rel_path, es_portada_pdf)."""
    slug = guia.get("slug", "guia")
    titulo = guia.get("titulo", "Guía PDF")
    use_pdf_cover = guia.get("portada_pdf") or slug == producto

    if use_pdf_cover:
        png_src = portada_imagen_path(producto)
        if png_src:
            dest = out_dir / f"portada-{slug}.png"
            shutil.copy2(png_src, dest)
            return dest.name, f"assets/{dest.name}", True

        meta = load_json(producto_meta_path(producto), {}) or {}
        subtitulo = meta.get("subtitulo_portada", "El principio de Pareto")
        if meta.get("titulo_comercial"):
            titulo = meta.get("titulo_comercial", titulo)
        fname = _write(
            out_dir / f"portada-{slug}.svg",
            portada_pareto_pdf_svg(titulo, f"{subtitulo} · Antoine Delers"),
        )
        return fname, f"assets/{fname}", True

    accents = [_c(marca, "gold", "#c9a962"), "#a68b5b", "#8b7355"]
    idx = hash(slug) % len(accents)
    fname = _write(
        out_dir / f"portada-{slug}.svg",
        portada_svg(marca, titulo, accent_bar=accents[idx]),
    )
    return fname, f"assets/{fname}", False


def portada_libro_svg(marca: dict, titulo: str, autor: str = "") -> str:
    """Portada serie — sin marco blanco; fondo transparente para el carrusel."""
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    gold = _c(marca, "gold", "#c9a962")
    muted = _c(marca, "muted", "#6b6560")
    line1 = titulo[:36]
    line2 = titulo[36:72] if len(titulo) > 36 else ""
    autor_line = autor[:40] if autor else "Serie Aplicar en tu rol"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 440" role="img">
  <rect x="0" y="0" width="5" height="440" fill="{gold}"/>
  <text x="20" y="72" fill="{gold}" font-family="system-ui,sans-serif" font-size="8" letter-spacing="0.14em">SERIE · LIBRO FUENTE</text>
  <text x="20" y="108" fill="{charcoal}" font-family="Georgia,serif" font-size="16" font-weight="700">{line1}</text>
  <text x="20" y="134" fill="{charcoal}" font-family="Georgia,serif" font-size="16" font-weight="700">{line2}</text>
  <text x="20" y="360" fill="{muted}" font-family="system-ui,sans-serif" font-size="10">{autor_line}</text>
  <text x="20" y="384" fill="{gold}" font-family="system-ui,sans-serif" font-size="9" letter-spacing="0.12em">APLICAR EN TU ROL</text>
</svg>"""


def generate_mock_assets(out_dir: Path, marca: dict, *, producto: str = "pareto") -> dict[str, str]:
    catalogo = marca.get("catalogo_guias") or [marca.get("producto_piloto", {})]
    serie = marca.get("serie_libros") or catalogo
    assets: dict[str, str] = {}
    carousel: list[dict] = []

    # Carrusel = solo libros de la serie
    for i, libro in enumerate(serie):
        slug = libro.get("slug", f"libro-{i}")
        titulo = libro.get("titulo", "Libro")
        autor = libro.get("autor", "")
        fname = _write(
            out_dir / f"libro-{slug}.svg",
            portada_libro_svg(marca, titulo, autor),
        )
        rel = f"assets/{fname}"
        assets[f"libro_{slug}"] = rel
        carousel.append({
            "tipo": "libro",
            "slug": slug,
            "titulo": titulo,
            "subtitulo": autor or libro.get("tagline", "Aplica en tu rol"),
            "precio": "",
            "disponible": libro.get("disponible", True),
            "src": rel,
        })

    # Portadas por guía (libro × rol) — productos reales
    piloto_slug = marca.get("producto_piloto", {}).get("slug", "pareto-psicopedagogas")
    accents = [_c(marca, "gold", "#c9a962"), "#a68b5b", "#8b7355"]
    for i, guia in enumerate(catalogo):
        slug = guia.get("slug", f"guia-{i}")
        titulo = guia.get("titulo", "Guía PDF")
        if guia.get("portada_pdf") or slug == piloto_slug:
            _, rel, _ = _portada_for_guia(
                out_dir, marca,
                {"slug": "pareto", "titulo": titulo, "portada_pdf": True},
                producto="pareto",
            )
            # Renombrar a slug de la guía
            src_path = out_dir / rel.replace("assets/", "")
            dest_path = out_dir / f"portada-{slug}.png"
            if src_path.exists() and src_path.suffix == ".png":
                shutil.copy2(src_path, dest_path)
                rel = f"assets/portada-{slug}.png"
            elif src_path.exists():
                dest_path = out_dir / f"portada-{slug}.svg"
                shutil.copy2(src_path, dest_path)
                rel = f"assets/portada-{slug}.svg"
        else:
            fname = _write(
                out_dir / f"portada-{slug}.svg",
                portada_svg(marca, titulo, accent_bar=accents[i % len(accents)]),
            )
            rel = f"assets/{fname}"
        assets[f"portada_{slug}"] = rel

    assets["portada"] = assets.get(f"portada_{piloto_slug}", "")
    assets["mockup_movil"] = f"assets/{_write(out_dir / 'mockup-movil.svg', mockup_movil_svg(marca))}"
    lectura_src = Path(__file__).resolve().parent.parent / "data" / "vertice-pro" / "assets" / "landing-lectura-lado.png"
    if lectura_src.is_file():
        shutil.copy2(lectura_src, out_dir / "landing-lectura-lado.png")
        assets["imagen_lectura"] = "assets/landing-lectura-lado.png"
    assets["_carousel_json"] = carousel  # type: ignore[assignment]
    assets["_catalogo_guias_json"] = catalogo  # type: ignore[assignment]
    return assets

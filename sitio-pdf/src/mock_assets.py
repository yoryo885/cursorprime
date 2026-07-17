"""Genera assets SVG mock — estilo premium cálido (referencia FILJÓS)."""

from __future__ import annotations

from pathlib import Path


def _c(marca: dict, key: str, default: str) -> str:
    return marca.get("colores", {}).get(key, default)


def _write(path: Path, svg: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg.strip(), encoding="utf-8")
    return path.name


def hero_svg(marca: dict) -> str:
    bg = _c(marca, "cream_dark", "#f0ebe3")
    gold = _c(marca, "gold", "#c9a962")
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    tag = marca.get("tagline", "Aplicar en tu rol")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 720" role="img">
  <rect width="1400" height="720" fill="{bg}"/>
  <rect x="0" y="580" width="1400" height="140" fill="#fff" opacity="0.6"/>
  <circle cx="200" cy="360" r="280" fill="{gold}" opacity="0.08"/>
  <circle cx="1200" cy="200" r="200" fill="{gold}" opacity="0.06"/>
  <rect x="80" y="80" width="520" height="560" rx="2" fill="#fff" stroke="#e8e4df" stroke-width="1"/>
  <rect x="100" y="100" width="480" height="400" fill="{bg}"/>
  <rect x="180" y="180" width="160" height="220" rx="3" fill="{charcoal}"/>
  <rect x="172" y="188" width="160" height="220" rx="3" fill="#fff"/>
  <text x="252" y="280" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="14" font-weight="700">PDF</text>
  <text x="252" y="310" text-anchor="middle" fill="{gold}" font-family="system-ui" font-size="10">Guía</text>
  <text x="680" y="280" fill="{charcoal}" font-family="Georgia,serif" font-size="48" font-weight="400" letter-spacing="0.08em">VÉRTICE PRO</text>
  <text x="680" y="340" fill="#6b6560" font-family="system-ui,sans-serif" font-size="22">{tag}</text>
  <text x="680" y="400" fill="#6b6560" font-family="system-ui" font-size="16">Guías PDF · Descarga instantánea</text>
  <rect x="680" y="440" width="180" height="48" fill="{charcoal}"/>
  <text x="770" y="470" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="13" letter-spacing="0.06em">VER GUÍAS</text>
</svg>"""


def portada_svg(marca: dict, producto: dict) -> str:
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    gold = _c(marca, "gold", "#c9a962")
    bg = _c(marca, "cream_dark", "#f0ebe3")
    titulo = producto.get("titulo", "Guía PDF")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 640" role="img">
  <rect width="480" height="640" fill="{bg}"/>
  <rect x="40" y="40" width="400" height="560" fill="#fff" stroke="#e8e4df"/>
  <rect x="56" y="56" width="368" height="480" fill="{charcoal}"/>
  <rect x="48" y="48" width="368" height="480" fill="#fff"/>
  <rect x="48" y="48" width="6" height="480" fill="{gold}"/>
  <text x="80" y="140" fill="{charcoal}" font-family="Georgia,serif" font-size="20" font-weight="700">{titulo[:30]}</text>
  <text x="80" y="175" fill="{charcoal}" font-family="Georgia,serif" font-size="20" font-weight="700">{titulo[30:58] if len(titulo)>30 else ''}</text>
  <text x="80" y="520" fill="{gold}" font-family="system-ui" font-size="11" letter-spacing="0.1em">APLICAR EN TU ROL</text>
  <text x="80" y="545" fill="#6b6560" font-family="system-ui" font-size="10">VÉRTICE PRO</text>
</svg>"""


def mockup_movil_svg(marca: dict) -> str:
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    gold = _c(marca, "gold", "#c9a962")
    bg = _c(marca, "bg", "#faf8f5")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 640" role="img">
  <rect x="30" y="16" width="260" height="580" rx="32" fill="{charcoal}"/>
  <rect x="42" y="48" width="236" height="516" rx="2" fill="{bg}"/>
  <text x="160" y="80" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="11" letter-spacing="0.12em">VÉRTICE PRO</text>
  <rect x="62" y="110" width="196" height="140" fill="#fff" stroke="#e8e4df"/>
  <rect x="62" y="110" width="196" height="140" fill="{charcoal}" opacity="0.04"/>
  <text x="160" y="185" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="10">Pareto</text>
  <rect x="62" y="280" width="140" height="6" rx="2" fill="#e8e4df"/>
  <rect x="62" y="300" width="100" height="6" rx="2" fill="#e8e4df"/>
  <rect x="62" y="340" width="196" height="40" fill="{charcoal}"/>
  <text x="160" y="366" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="10">Comprar PDF</text>
  <ellipse cx="160" cy="36" rx="36" ry="5" fill="#333"/>
</svg>"""


def generate_mock_assets(out_dir: Path, marca: dict) -> dict[str, str]:
    producto = marca.get("producto_piloto", {})
    return {
        "hero": _write(out_dir / "hero.svg", hero_svg(marca)),
        "portada": _write(out_dir / "portada-producto.svg", portada_svg(marca, producto)),
        "mockup_movil": _write(out_dir / "mockup-movil.svg", mockup_movil_svg(marca)),
    }

"""SVG decorativos simples — sin texto (el copy va solo en HTML)."""

from __future__ import annotations

from pathlib import Path


def _c(marca: dict, key: str, default: str) -> str:
    return marca.get("colores", {}).get(key, default)


def _write(path: Path, svg: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg.strip(), encoding="utf-8")
    return path.name


def hero_bg_svg(marca: dict) -> str:
    """Fondo suave sin texto — opcional."""
    bg = _c(marca, "cream_dark", "#f0ebe3")
    gold = _c(marca, "gold", "#c9a962")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice" role="presentation">
  <rect width="800" height="600" fill="{bg}"/>
  <circle cx="650" cy="120" r="180" fill="{gold}" opacity="0.07"/>
  <circle cx="100" cy="480" r="140" fill="{gold}" opacity="0.05"/>
</svg>"""


def portada_svg(marca: dict, producto: dict) -> str:
    charcoal = _c(marca, "charcoal", "#1a1a1a")
    gold = _c(marca, "gold", "#c9a962")
    bg = _c(marca, "cream_dark", "#f0ebe3")
    titulo = producto.get("titulo", "Guía PDF")
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
  <text x="140" y="155" text-anchor="middle" fill="{charcoal}" font-family="Georgia,serif" font-size="9">Pareto</text>
  <rect x="52" y="230" width="120" height="5" rx="2" fill="#e8e4df"/>
  <rect x="52" y="248" width="90" height="5" rx="2" fill="#e8e4df"/>
  <rect x="52" y="280" width="176" height="36" fill="{charcoal}"/>
  <text x="140" y="303" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="9">Comprar PDF</text>
</svg>"""


def generate_mock_assets(out_dir: Path, marca: dict) -> dict[str, str]:
    producto = marca.get("producto_piloto", {})
    return {
        "hero_bg": _write(out_dir / "hero-bg.svg", hero_bg_svg(marca)),
        "portada": _write(out_dir / "portada-producto.svg", portada_svg(marca, producto)),
        "mockup_movil": _write(out_dir / "mockup-movil.svg", mockup_movil_svg(marca)),
    }

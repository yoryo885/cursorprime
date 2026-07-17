"""Genera assets SVG mock profesionales (sin API)."""

from __future__ import annotations

from pathlib import Path


def _write(path: Path, svg: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg.strip(), encoding="utf-8")
    return path.name


def hero_svg(marca: dict) -> str:
    navy = marca.get("colores", {}).get("navy", "#1e3a5f")
    accent = marca.get("colores", {}).get("accent", "#2563eb")
    name = marca.get("marca", "Vértice Pro")
    tag = marca.get("tagline", "Aplicar en tu rol")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" role="img">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{navy}"/>
      <stop offset="100%" style="stop-color:#2d4a6f"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="980" cy="120" r="180" fill="{accent}" opacity="0.12"/>
  <circle cx="1050" cy="480" r="120" fill="#059669" opacity="0.1"/>
  <text x="80" y="200" fill="#fff" font-family="Georgia,serif" font-size="52" font-weight="700">{name}</text>
  <text x="80" y="280" fill="#cbd5e1" font-family="system-ui,sans-serif" font-size="28">Guías PDF · {tag}</text>
  <text x="80" y="340" fill="#94a3b8" font-family="system-ui,sans-serif" font-size="20">Descarga instantánea para profesionales</text>
  <rect x="720" y="140" width="200" height="280" rx="6" fill="#fff" opacity="0.95"/>
  <rect x="710" y="150" width="200" height="280" rx="6" fill="#e8eef5"/>
  <text x="810" y="280" text-anchor="middle" fill="{navy}" font-family="Georgia,serif" font-size="16" font-weight="700">PDF</text>
  <text x="810" y="310" text-anchor="middle" fill="{accent}" font-family="system-ui" font-size="12">Guía práctica</text>
</svg>"""


def portada_svg(marca: dict, producto: dict) -> str:
    navy = marca.get("colores", {}).get("navy", "#1e3a5f")
    accent = marca.get("colores", {}).get("accent", "#2563eb")
    titulo = producto.get("titulo", "Guía PDF")
    lines = titulo.split(" en ")
    line1 = lines[0] if lines else titulo
    line2 = ("en " + lines[1]) if len(lines) > 1 else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 560" role="img">
  <rect width="400" height="560" fill="{navy}"/>
  <rect x="0" y="0" width="8" height="560" fill="{accent}"/>
  <text x="40" y="120" fill="#fff" font-family="Georgia,serif" font-size="22" font-weight="700">{line1[:28]}</text>
  <text x="40" y="155" fill="#fff" font-family="Georgia,serif" font-size="22" font-weight="700">{line1[28:56] if len(line1)>28 else ''}</text>
  <text x="40" y="200" fill="{accent}" font-family="system-ui" font-size="14">{line2[:35]}</text>
  <text x="40" y="480" fill="#94a3b8" font-family="system-ui" font-size="11">Serie Aplicar en tu rol</text>
  <text x="40" y="500" fill="#64748b" font-family="system-ui" font-size="10">Vértice Pro</text>
</svg>"""


def mockup_movil_svg(marca: dict) -> str:
    navy = marca.get("colores", {}).get("navy", "#1e3a5f")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img">
  <rect x="40" y="20" width="280" height="580" rx="36" fill="#1a1a1a"/>
  <rect x="52" y="60" width="256" height="520" rx="4" fill="#f8f9fb"/>
  <rect x="52" y="60" width="256" height="48" fill="{navy}"/>
  <text x="180" y="90" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="12">Vértice Pro</text>
  <rect x="72" y="130" width="216" height="120" rx="4" fill="{navy}" opacity="0.9"/>
  <text x="180" y="185" text-anchor="middle" fill="#fff" font-family="Georgia,serif" font-size="11">Pareto · 10 semanas</text>
  <rect x="72" y="270" width="196" height="8" rx="2" fill="#e2e8f0"/>
  <rect x="72" y="290" width="160" height="8" rx="2" fill="#e2e8f0"/>
  <rect x="72" y="310" width="180" height="8" rx="2" fill="#e2e8f0"/>
  <rect x="72" y="360" width="216" height="36" rx="6" fill="#2563eb"/>
  <text x="180" y="383" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="11">Descargar PDF</text>
  <ellipse cx="180" cy="42" rx="40" ry="6" fill="#333"/>
</svg>"""


def generate_mock_assets(out_dir: Path, marca: dict) -> dict[str, str]:
    producto = marca.get("producto_piloto", {})
    assets = {
        "hero": _write(out_dir / "hero.svg", hero_svg(marca)),
        "portada": _write(out_dir / "portada-producto.svg", portada_svg(marca, producto)),
        "mockup_movil": _write(out_dir / "mockup-movil.svg", mockup_movil_svg(marca)),
    }
    return assets

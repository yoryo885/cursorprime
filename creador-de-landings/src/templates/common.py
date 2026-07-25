"""Helpers compartidos de templates HTML."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from src.config import ROOT


def _e(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def _fonts() -> str:
    return (
        '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600'
        '&family=Outfit:wght@400;500;600&display=swap" rel="stylesheet"/>'
    )


def _palette_vars(b: dict) -> str:
    p = b.get("paleta") or {}
    ink = p.get("ink") or "#1b222c"
    paper = p.get("paper") or "#f4f1ec"
    accent = p.get("accent") or "#2a3544"
    muted = p.get("muted") or "#7a847c"
    hero = p.get("hero") or ink
    return (
        f"--ink:{ink}; --paper:{paper}; --accent:{accent}; --muted:{muted}; "
        f"--hero:{hero};"
    )


def resolve_hero_imagen(path: str) -> str:
    """Solo usa hero_imagen si el archivo existe (evita CSS roto)."""
    if not path:
        return ""
    p = Path(path)
    candidates = [
        p,
        ROOT / path,
        ROOT / "data" / "demo-cliente" / "output" / path,
        ROOT / "assets" / Path(path).name,
    ]
    for c in candidates:
        if c.is_file():
            # prefer relative web path if under output
            return path
    return ""


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

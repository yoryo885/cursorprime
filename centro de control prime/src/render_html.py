"""Genera panel HTML — dashboard compacto y profesional."""

from __future__ import annotations

import json
from html import escape

from src.panel_assets import HUD_CSS, HUD_JS
from src.panel_data import prepare_panel_data


def _href(prefix: str, path: str) -> str:
    if not path:
        return ""
    p = path.replace("\\", "/").lstrip("/")
    if prefix in ("", "./") and p.startswith("analisis-de-proyectos/"):
        p = p[len("analisis-de-proyectos/") :]
    return prefix + p


def _badge(val: str, kind: str = "") -> str:
    v = str(val).lower()
    cls = kind or (v if v in ("live", "mock", "viable", "condicional", "hecho", "parcial", "falta") else "")
    return f"<span class='badge {cls}'>{escape(str(val).upper())}</span>"


def _hero_compact(item: dict, *, title: str | None = None, meta_prefix: str = "", href_prefix: str = "../") -> str:
    if not item:
        return ""
    ver = str(item.get("veredicto", "—"))
    ver_cls = ver.lower() if ver.lower() in ("viable", "condicional") else ""
    informe = item.get("informe", "")
    link = f"<a href='{_href(href_prefix, informe)}'>Informe completo →</a>" if informe else ""
    tema = str(item.get("tema", ""))
    if len(tema) > 70:
        tema = tema[:67] + "…"
    h = title or str(item.get("nombre") or item.get("slug", ""))
    fetch = item.get("fetch", "mock")
    return f"""
    <div class="hero-compact">
      <div class="hero-top">
        <h2>{escape(h)}</h2>
        <div class="meta">{meta_prefix}{escape(item.get('fecha', '—'))} · {_badge(fetch, 'live' if fetch == 'live' else 'mock')}</div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><div class="lbl">Fuentes</div><div class="val">{item.get('fuentes', 0)}</div></div>
        <div class="hero-stat"><div class="lbl">Veredicto</div><div class="val">{_badge(ver, ver_cls)}</div></div>
        <div class="hero-stat"><div class="lbl">Score</div><div class="val">{item.get('score', '—')}</div></div>
        <div class="hero-stat"><div class="lbl">Oportun.</div><div class="val">{item.get('oportunidades', 0)}</div></div>
      </div>
      <p class="resumen"><strong>Tema:</strong> {escape(tema)} — {escape(item.get('resumen', ''))}</p>
      {link}
    </div>"""


def _kpi_row(metricas: list[dict], keys: list[str] | None = None) -> str:
    ids = keys or ["analisis", "evaluaciones", "cola_pendientes", "modulos_ok", "clientes", "avance"]
    by_id = {m["id"]: m for m in metricas}
    html = ""
    for kid in ids:
        m = by_id.get(kid)
        if not m:
            continue
        html += f"""<div class="kpi"><div class="kpi-val">{m['valor']}</div><div class="kpi-lbl">{escape(m['titulo'])}</div></div>"""
    if "avance" in ids and "avance" not in by_id:
        pass
    return html


def _flujo_compact(flujo: list[dict]) -> str:
    goto = {1: ("operaciones", "analisis"), 2: ("operaciones", "pendientes"), 3: ("operaciones", "evaluaciones"), 4: ("sistema", "")}
    html = '<div class="flujo-compact">'
    for p in flujo:
        g, sub = goto.get(p["paso"], ("resumen", ""))
        sub_attr = f' data-sub="{sub}"' if sub else ""
        html += f"""
        <div class="flujo-pill" data-goto="{g}"{sub_attr}>
          <div class="step">Paso {p['paso']}</div>
          <div class="name">{escape(p.get('nombre_corto') or p['nombre'])}</div>
          <div class="cnt">{p['count']}</div>
        </div>"""
    html += "</div>"
    return html


def _hero_card(item: dict, *, title: str | None = None, meta_prefix: str = "", href_prefix: str = "../") -> str:
    fetch = item.get("fetch", "mock")
    ver = str(item.get("veredicto", "—"))
    ver_cls = ver.lower() if ver.lower() in ("viable", "condicional") else ""
    informe = item.get("informe", "")
    link = f"<a class='informe-link' href='{_href(href_prefix, informe)}'>Ver informe →</a>" if informe else ""
    h = title or str(item.get("nombre") or item.get("slug", ""))
    tema = str(item.get("tema", ""))
    return f"""
    <article class="analisis-hero">
      <h2>{escape(h)}</h2>
      <div class="meta">{meta_prefix}{escape(item.get('fecha', '—'))} · {_badge(fetch, 'live' if fetch == 'live' else 'mock')}</div>
      <div class="analisis-stat stat-tema"><div class="lbl">Tema</div><div class="val">{escape(tema)}</div></div>
      <div class="analisis-hero-grid">
        <div class="analisis-stat"><div class="lbl">Fuentes</div><div class="val">{item.get('fuentes', 0)}</div></div>
        <div class="analisis-stat"><div class="lbl">Veredicto</div><div class="val">{_badge(ver, ver_cls)}</div></div>
        <div class="analisis-stat"><div class="lbl">Score</div><div class="val">{item.get('score', '—')}</div></div>
        <div class="analisis-stat"><div class="lbl">Oportun.</div><div class="val">{item.get('oportunidades', 0)}</div></div>
      </div>
      <p class="analisis-resumen">{escape(item.get('resumen', ''))}</p>
      {link}
    </article>"""


def _viabilidad_heroes(viab: dict | None, *, href_prefix: str = "../") -> str:
    if not viab or not viab.get("items"):
        return '<p class="empty">Sin datos. <code>python3 panel_main.py viabilidad --live --refresh</code></p>'
    html = ""
    for capa in viab.get("capas") or []:
        proys = capa.get("proyectos") or []
        if not proys:
            continue
        cls = "producto" if capa.get("id") == "producto" else ""
        cards = "".join(
            _hero_card(p, title=str(p.get("nombre", "")), meta_prefix="Viabilidad mercado · ", href_prefix=href_prefix)
            for p in proys
        )
        html += f"""
        <div class="capa-block">
          <div class="capa-label {cls}">
            <h3>{escape(capa.get('titulo', ''))}</h3>
            <span>{capa.get('viables', 0)} viables · score {capa.get('score_promedio', 0)}</span>
          </div>
          <div class="analisis-heroes-grid">{cards}</div>
        </div>"""
    return html


def _viabilidad_table(proyectos: list[dict]) -> str:
    if not proyectos:
        return '<p class="empty">Sin datos. Ejecuta <code>python3 panel_main.py viabilidad --live --refresh</code></p>'
    rows = ""
    for p in proyectos:
        fetch = p.get("fetch", "mock")
        ver = str(p.get("veredicto", "—"))
        ver_cls = ver.lower() if ver.lower() in ("viable", "condicional") else ""
        informe = p.get("informe", "")
        link = f"<a href='../../{escape(informe)}'>↗</a>" if informe else "—"
        rows += f"""
        <tr class="expandable">
          <td><strong>{escape(p.get('nombre', ''))}</strong></td>
          <td>{_badge(fetch, 'live' if fetch == 'live' else 'mock')}</td>
          <td>{p.get('fuentes', 0)}</td>
          <td>{_badge(ver, ver_cls)}</td>
          <td>{p.get('score', '—')}</td>
          <td>{p.get('oportunidades', 0)}</td>
          <td>{link}</td>
        </tr>
        <tr class="detail-row" style="display:none"><td colspan="7">{escape(p.get('resumen', ''))}</td></tr>"""
    return f"""
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr>
          <th>Proyecto</th><th>Fetch</th><th>Fuentes</th><th>Veredicto</th><th>Score</th><th>Opp</th><th></th>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def _viabilidad_capas(viab: dict | None) -> str:
    return _viabilidad_heroes(viab)


def _modulos_table(secciones: list[dict]) -> str:
    rows = ""
    for sec in secciones:
        capa = sec.get("titulo", "")
        for m in sec.get("modulos") or []:
            est = m.get("estado", "parcial")
            pct = m.get("avance_pct", 0)
            pend = "; ".join(m.get("pendientes") or []) or "—"
            rows += f"""
            <tr class="expandable">
              <td><span style="color:var(--muted);font-size:0.68rem">{escape(capa)}</span><br><strong>{escape(m.get('nombre',''))}</strong></td>
              <td><code>{escape(m.get('carpeta',''))}</code></td>
              <td>{_badge(est, est)}</td>
              <td><span class="bar-mini"><span class="bar-mini-fill" style="width:{pct}%"></span></span> {pct}%</td>
              <td style="color:var(--yellow);font-size:0.72rem">{escape(pend[:80])}{'…' if len(pend)>80 else ''}</td>
            </tr>
            <tr class="detail-row" style="display:none"><td colspan="5">{escape(pend)}</td></tr>"""
    if not rows:
        return '<p class="empty">Sin módulos.</p>'
    return f"""
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr><th>Módulo</th><th>Carpeta</th><th>Estado</th><th>Avance</th><th>Pendientes</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def _table_simple(items: list[dict], cols: list[tuple[str, str]], *, badge: str | None = None) -> str:
    if not items:
        return '<p class="empty">Nada aquí todavía.</p>'
    head = "".join(f"<th>{escape(l)}</th>" for _, l in cols)
    rows = ""
    for it in items[:30]:
        cells = ""
        for key, _ in cols:
            val = it.get(key, "")
            if key == "titulo" and len(str(val)) > 55:
                val = str(val)[:52] + "…"
            if badge == key and val:
                cells += f"<td>{_badge(str(val), str(val).lower())}</td>"
            else:
                cells += f"<td>{escape(str(val))}</td>"
        rows += f"<tr>{cells}</tr>"
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def _analisis_mercado_table(items: list[dict], *, href_prefix: str = "../") -> str:
    if not items:
        return '<p class="empty">Sin investigaciones.</p>'
    rows = ""
    for it in items:
        fetch = it.get("fetch", "mock")
        ver = str(it.get("veredicto", "—"))
        ver_cls = ver.lower() if ver.lower() in ("viable", "condicional") else ""
        informe = it.get("informe", "")
        link = f"<a href='{_href(href_prefix, informe)}'>↗</a>" if informe else "—"
        rows += f"""<tr>
          <td>{escape(it.get('tema',''))}</td>
          <td><code>{escape(it.get('slug',''))}</code></td>
          <td>{_badge(fetch, 'live' if fetch=='live' else 'mock')}</td>
          <td>{it.get('fuentes',0)}</td>
          <td>{_badge(ver, ver_cls)}</td>
          <td>{it.get('score','—')}</td>
          <td>{link}</td>
        </tr>"""
    return f"""<div class="tbl-wrap"><table class="tbl">
      <thead><tr><th>Tema</th><th>Slug</th><th>Fetch</th><th>Fuentes</th><th>Veredicto</th><th>Score</th><th></th></tr></thead>
      <tbody>{rows}</tbody></table></div>"""


def _embudo_mini(embudo: list[dict], *, href_prefix: str = "../", index_path: str = "") -> str:
    rows = ""
    for e in embudo:
        pct = 100 if e.get("listo") else 30
        url = _href(href_prefix, e.get("path", ""))
        link = f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(e["nombre"])}</a>' if url else escape(e["nombre"])
        rows += f"""
        <div class="embudo-mini-row">
          <span>{e['paso']}</span>
          <div><div style="font-size:0.72rem;margin-bottom:3px">{link}</div>
          <div class="embudo-mini-bar"><div class="embudo-mini-fill" style="width:{pct}%"></div></div></div>
          <span style="text-align:right;color:var(--accent)">{pct}%</span>
        </div>"""
    idx = _href(href_prefix, index_path)
    footer = f'<p class="embudo-mini-foot"><button type="button" class="link-btn" data-view="embudo">Ver embudo completo →</button></p>' if index_path else ""
    return f'<div class="embudo-mini">{rows}</div>{footer}'


def _embudo_view(embudo: list[dict], *, href_prefix: str, index_path: str) -> str:
    steps = ""
    step_urls: list[dict] = []
    for e in embudo:
        url = _href(href_prefix, e.get("path", ""))
        done = " step-done" if e.get("listo") else ""
        step_urls.append({"paso": e["paso"], "url": url, "title": e["nombre"]})
        steps += f"""
        <button type="button" class="embudo-step{done}" data-embudo-url="{escape(url)}"
          data-embudo-title="{escape(e['nombre'])}" data-embudo-paso="{e['paso']}">
          <span class="embudo-step-num">{e['paso']}</span>
          <h3>{escape(e['nombre'])}</h3>
          <p>{escape(e.get('desc', ''))}</p>
          <span class="embudo-step-meta">{_badge('demo' if e.get('estado') == 'demo' else e.get('estado', '—'), 'mock')}</span>
        </button>"""
    idx = _href(href_prefix, index_path)
    flow = "".join(
        f'<span class="embudo-flow-item{" done" if e.get("listo") else ""}">{e["paso"]}</span>'
        + ('<span class="embudo-flow-arrow">→</span>' if i < len(embudo) - 1 else "")
        for i, e in enumerate(embudo)
    )
    pendientes = "".join(
        f"<li><strong>Paso {e['paso']}:</strong> {escape(e.get('falta', ''))}</li>" for e in embudo if e.get("falta")
    )
    steps_json = json.dumps(step_urls, ensure_ascii=False).replace("</", "<\\/")
    return f"""
    <div id="embudo-shell" class="embudo-shell" data-index-url="{escape(idx)}" data-steps="{escape(steps_json)}">
      <div id="embudo-overview">
        <div class="embudo-intro">
          <p>Cliente demo <strong>Clínica Sol</strong> · flujo informe → propuesta → web → WhatsApp.
          Cada paso se abre aquí mismo; puedes seguir con anterior / siguiente.</p>
          <button type="button" class="btn-outline" data-embudo-url="{escape(idx)}"
            data-embudo-title="Índice del embudo" data-embudo-paso="0">Abrir índice del embudo</button>
        </div>
        <div class="embudo-flow">{flow}</div>
        <div class="embudo-steps">{steps}</div>
        <div class="card" style="margin-top:12px">
          <div class="card-head"><h2>Para producción</h2><span class="hint">Qué falta en cada paso</span></div>
          <div class="card-body"><ul class="embudo-pendientes">{pendientes}</ul></div>
        </div>
      </div>
      <div id="embudo-viewer" class="embudo-viewer" hidden>
        <div class="embudo-toolbar">
          <button type="button" class="embudo-tool" data-embudo-back>← Índice panel</button>
          <span id="embudo-viewer-title" class="embudo-viewer-title">—</span>
          <div class="embudo-tool-group">
            <button type="button" class="embudo-tool" data-embudo-prev disabled>← Anterior</button>
            <button type="button" class="embudo-tool" data-embudo-next disabled>Siguiente →</button>
            <a id="embudo-external" class="embudo-tool embudo-tool-link" href="#" target="_blank" rel="noopener">Nueva pestaña ↗</a>
          </div>
        </div>
        <iframe id="embudo-frame" class="embudo-frame" title="Vista previa embudo comercial"></iframe>
      </div>
    </div>"""


def _rent_prioridad_badge(p: str) -> tuple[str, str]:
    m = {
        "alta": ("Alta", "rent-alta"),
        "media": ("Media", "rent-media"),
        "baja": ("Baja", "rent-baja"),
        "no crear": ("No crear", "rent-no"),
    }
    return m.get((p or "").lower(), ("—", "rent-media"))


def _rent_estado(item: dict) -> str:
    if item.get("bloqueo"):
        return f'<span class="estado-tag falta">{escape(item["bloqueo"])}</span>'
    infra = item.get("infra") or []
    if infra:
        return f'<span class="estado-tag listo">Infra: {escape(", ".join(infra[:2]))}{"…" if len(infra) > 2 else ""}</span>'
    return '<span class="estado-tag">Sin infra</span>'


def _rentabilidad_view(data: dict) -> str:
    if not data or not data.get("ranking"):
        return '<p class="empty">Sin ranking. Fuente: <code>ideas de proyectos/RANKING_RENTABILIDAD.json</code></p>'
    top3 = "".join(f"<li>{escape(x)}</li>" for x in data.get("top3_accion") or [])
    cards = ""
    for item in data.get("ranking") or []:
        label, cls = _rent_prioridad_badge(item.get("prioridad", ""))
        rank = item.get("rank")
        rank_txt = f"#{rank}" if rank else "—"
        score = item.get("score") or item.get("score_estimado") or "—"
        margen = item.get("margen_pct")
        margen_txt = f" · margen {margen}%" if margen else ""
        cards += f"""
        <article class="rent-card">
          <div class="rent-card-top">
            <span class="rent-rank">{rank_txt}</span>
            <span class="rent-badge {cls}">{label}</span>
          </div>
          <h3>{escape(item.get('titulo', ''))}</h3>
          <p class="rent-why">{escape(item.get('por_que', ''))}</p>
          <div class="rent-meta">Score {score}{margen_txt} · {_rent_estado(item)}</div>
        </article>"""
    conf = data.get("confidence_global", "—")
    fecha = data.get("generado_at", "—")
    return f"""
    <div class="rent-top3">
      <h2>Prioridad ahora</h2>
      <ol>{top3}</ol>
    </div>
    <div class="rent-leyenda">
      <span><i class="dot dot-alta"></i> Alta — primer $ rápido</span>
      <span><i class="dot dot-media"></i> Media — lento o bloqueado</span>
      <span><i class="dot dot-baja"></i> Baja — mucho esfuerzo</span>
      <span><i class="dot dot-no"></i> No crear</span>
    </div>
    <div class="rent-grid">{cards}</div>
    <p class="rent-footer">confidence {escape(str(conf))} · {escape(str(fecha))} · {escape(data.get('nota', ''))}</p>"""


def _clientes_table(clientes: list[dict]) -> str:
    if not clientes:
        return '<p class="empty">Sin clientes.</p>'
    rows = ""
    for c in clientes:
        proys = ", ".join(p["slug"] + (" ✓" if p.get("embudo") else "") for p in c.get("proyectos", []))
        rows += f"<tr><td>{escape(c['slug'])}</td><td>{escape(proys or '—')}</td><td>{len(c.get('proyectos',[]))}</td></tr>"
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Cliente</th><th>Proyectos</th><th>#</th></tr></thead><tbody>{rows}</tbody></table></div>'


def _folders_compact(carpetas: list[dict]) -> str:
    if not carpetas:
        return '<p class="empty">Sin carpetas.</p>'
    rows = ""
    for c in carpetas:
        cli = "CLI" if c.get("has_cli") else "—"
        subs = ", ".join(c.get("subcarpetas", [])[:6])
        rows += f"<tr><td>{escape(c['nombre'])}</td><td>{escape(c.get('tipo',''))}</td><td>{cli}</td><td style='font-size:0.72rem;color:var(--muted)'>{escape(subs)}</td></tr>"
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Carpeta</th><th>Tipo</th><th></th><th>Contenido</th></tr></thead><tbody>{rows}</tbody></table></div>'


def render_html(inv: dict, *, href_prefix: str = "../") -> str:
    d = prepare_panel_data(inv)
    data_json = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    gen = escape(d.get("generado_legible", ""))
    r = d.get("resumen", {})

    ultimo = d.get("analisis_ultimo")
    radar = d.get("radar_auto", {})
    hero = ""
    if ultimo:
        sem = radar.get("ultima_semana_ok") or ultimo.get("slug", "")
        hero = _hero_compact(
            ultimo,
            title=f"Radar KDP — {ultimo.get('slug', '')}",
            meta_prefix=f"Semana {escape(str(sem))} · ",
            href_prefix=href_prefix,
        )

    kpi = _kpi_row(d["metricas"], ["analisis", "evaluaciones", "pendientes", "modulos_ok", "clientes", "implementadas"])
    kpi += f'<div class="kpi"><div class="kpi-val">{d.get("avance",0)}%</div><div class="kpi-lbl">Avance cola</div></div>'

    viab = d.get("viabilidad_proyectos")
    viab_heroes = _viabilidad_heroes(viab, href_prefix=href_prefix)
    embudo = d.get("embudo_comercial", [])
    embudo_index = d.get("embudo_index", "")
    embudo_full = _embudo_view(embudo, href_prefix=href_prefix, index_path=embudo_index)
    rentabilidad = _rentabilidad_view(d.get("rentabilidad", {}))

    idea_cols = [("titulo", "Idea"), ("categoria", "Tipo")]
    eval_cols = [("titulo", "Idea"), ("estado", "Veredicto"), ("score", "Score")]

    skills = "".join(f'<span class="skill-chip">{escape(s)}</span>' for s in d.get("skills_instaladas", []))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <meta name="apple-mobile-web-app-capable" content="yes"/>
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
  <title>Centro de control · cursorprime</title>
  <script defer src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>{HUD_CSS}</style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="topbar-brand">
        <h1>Centro de control prime</h1>
        <p>cursorprime · actualizado {gen}</p>
      </div>
      <div class="topbar-actions">
        <button type="button" class="quick-btn" data-view="embudo">Embudo demo</button>
        <button type="button" class="quick-btn" data-view="rentabilidad">Rentabilidad</button>
        <code>panel_main.py refresh</code>
      </div>
    </header>

    <nav class="nav">
      <button class="nav-btn active" data-view="resumen">Resumen</button>
      <button class="nav-btn" data-view="modulos">Módulos</button>
      <button class="nav-btn" data-view="operaciones">Cola e ideas</button>
      <button class="nav-btn" data-view="sistema">Sistema</button>
    </nav>

    <!-- RESUMEN -->
    <section id="view-resumen" class="view active">
      <div class="kpi-row">{kpi}</div>
      <div class="grid-2" style="margin-bottom:12px">
        <div class="card">
          <div class="card-head"><h2>Flujo de trabajo</h2><span class="hint">Clic → ir al detalle</span></div>
          <div class="card-body">{_flujo_compact(d['flujo'])}</div>
        </div>
        <div class="card">
          <div class="card-head"><h2>Último radar KDP</h2><span class="hint">YouTube + web · live</span></div>
          <div class="card-body">{hero or '<p class="empty">Sin radar aún.</p>'}</div>
        </div>
      </div>
      <div class="grid-3">
        <div class="card"><div class="card-head"><h2>Cola de ideas</h2></div><div class="card-body chart-box"><canvas id="chartCola"></canvas></div></div>
        <div class="card"><div class="card-head"><h2>Estado módulos</h2></div><div class="card-body chart-box"><canvas id="chartModulos"></canvas></div></div>
        <div class="card"><div class="card-head"><h2>Producción</h2></div><div class="card-body chart-box"><canvas id="chartProd"></canvas></div></div>
      </div>
    </section>

    <!-- MÓDULOS + VIABILIDAD -->
    <section id="view-modulos" class="view">
      <div class="card" style="margin-bottom:12px">
        <div class="card-head"><h2>Análisis de viabilidad</h2><span class="hint">YouTube + web · formato radar</span></div>
        <div class="card-body">{viab_heroes}</div>
      </div>
      <div class="card">
        <div class="card-head"><h2>Estado de implementación</h2><span class="hint">Clic fila → pendientes</span></div>
        <div class="card-body">{_modulos_table(d.get('modulos_secciones', []))}</div>
      </div>
    </section>

    <!-- OPERACIONES -->
    <section id="view-operaciones" class="view">
      <div class="card">
        <div class="card-head"><h2>Cola, evaluaciones e investigaciones</h2></div>
        <div class="card-body" id="operaciones">
          <div class="subnav">
            <button class="active" data-sub="pendientes">Sin revisar ({r.get('cola_pendientes',0)})</button>
            <button data-sub="evaluaciones">Evaluaciones ({r.get('evaluaciones',0)})</button>
            <button data-sub="analisis">Investigaciones ({r.get('analisis',0)})</button>
            <button data-sub="implementadas">Implementadas ({r.get('cola_implementadas',0)})</button>
            <button data-sub="espera">Pospuestas ({r.get('cola_en_espera',0)})</button>
          </div>
          <div id="operaciones-pendientes" class="subpanel active">{_table_simple(d.get('pendientes',[]), idea_cols)}</div>
          <div id="operaciones-evaluaciones" class="subpanel">{_table_simple(d.get('evaluaciones',[]), eval_cols, badge='estado')}</div>
          <div id="operaciones-analisis" class="subpanel">{_analisis_mercado_table(d.get('analisis_detalle',[]), href_prefix=href_prefix)}</div>
          <div id="operaciones-implementadas" class="subpanel">{_table_simple(d.get('implementadas',[]), idea_cols)}</div>
          <div id="operaciones-espera" class="subpanel">{_table_simple(d.get('en_espera',[]), idea_cols)}</div>
        </div>
      </div>
    </section>

    <!-- EMBUDO DEMO -->
    <section id="view-embudo" class="view">
      <div class="card">
        <div class="card-head"><h2>Embudo comercial — Clínica Sol</h2><span class="hint">4 entregables HTML · DEMO</span></div>
        <div class="card-body">{embudo_full}</div>
      </div>
    </section>

    <!-- RENTABILIDAD -->
    <section id="view-rentabilidad" class="view">
      <div class="card">
        <div class="card-head"><h2>Ideas por crear — rentabilidad</h2><span class="hint">RANKING_RENTABILIDAD.json</span></div>
        <div class="card-body">{rentabilidad}</div>
      </div>
    </section>

    <!-- SISTEMA -->
    <section id="view-sistema" class="view">
      <div class="grid-2">
        <div class="card">
          <div class="card-head"><h2>Embudo comercial</h2><span class="hint">demo clinica-sol</span></div>
          <div class="card-body">{_embudo_mini(embudo, href_prefix=href_prefix, index_path=embudo_index)}</div>
        </div>
        <div class="card">
          <div class="card-head"><h2>Clientes</h2></div>
          <div class="card-body">{_clientes_table(d.get('clientes',[]))}</div>
        </div>
      </div>
      <div class="card" style="margin-top:12px">
        <div class="card-head"><h2>Carpetas cursorprime</h2></div>
        <div class="card-body">{_folders_compact(d.get('carpetas',[]))}</div>
      </div>
      <div class="card" style="margin-top:12px">
        <div class="card-head"><h2>Skills instaladas</h2><span class="hint">{len(d.get('skills_instaladas',[]))} skills</span></div>
        <div class="card-body"><div class="skills-row">{skills or '<span class="empty">Ninguna</span>'}</div></div>
      </div>
    </section>

    <footer class="footer">
      Solo lectura · Viabilidad: <code>python3 panel_main.py viabilidad --live --refresh</code>
    </footer>
  </div>

  <script>window.INVENTARIO = {data_json};</script>
  <script>{HUD_JS}</script>
</body>
</html>"""

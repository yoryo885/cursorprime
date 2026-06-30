"""CSS y JS del panel — dashboard compacto y profesional."""

HUD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg: #0d1117;
  --surface: #161b22;
  --surface2: #1c2128;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #8b949e;
  --accent: #58a6ff;
  --green: #3fb950;
  --yellow: #d29922;
  --red: #f85149;
  --purple: #a371f7;
  --radius: 8px;
  --font: 'Inter', system-ui, sans-serif;
}

html, body { margin: 0; min-height: 100%; min-height: -webkit-fill-available; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  font-size: 13px;
  line-height: 1.45;
  min-height: 100vh;
  min-height: -webkit-fill-available;
  -webkit-text-size-adjust: 100%;
  overflow-x: hidden;
}

.app {
  max-width: 1280px; margin: 0 auto;
  padding: max(16px, env(safe-area-inset-top, 0px)) max(20px, env(safe-area-inset-right, 0px)) max(40px, env(safe-area-inset-bottom, 0px)) max(20px, env(safe-area-inset-left, 0px));
}

/* —— Topbar —— */
.topbar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 12px 20px;
  padding-bottom: 14px; border-bottom: 1px solid var(--border); margin-bottom: 14px;
}
.topbar-brand h1 { margin: 0; font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; }
.topbar-brand p { margin: 2px 0 0; font-size: 0.75rem; color: var(--muted); }
.topbar-actions { margin-left: auto; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.topbar-actions a, .topbar-actions code, .topbar-actions .quick-btn {
  font-size: 0.72rem; color: var(--accent); text-decoration: none;
  padding: 8px 12px; min-height: 44px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface);
  -webkit-tap-highlight-color: transparent; touch-action: manipulation;
}
.topbar-actions a:hover, .topbar-actions .quick-btn:hover { border-color: var(--accent); background: var(--surface2); cursor: pointer; }
.topbar-actions .quick-btn { font-family: inherit; }
.topbar-actions code { color: var(--muted); font-family: ui-monospace, monospace; }
.link-btn {
  font-family: inherit; font-size: 0.72rem; color: var(--accent); background: none; border: none;
  padding: 0; cursor: pointer; text-decoration: none;
}
.link-btn:hover { text-decoration: underline; }

/* —— Nav —— */
.nav {
  display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 16px;
  padding: 4px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
}
.nav-btn {
  padding: 10px 14px; min-height: 44px; font-size: 0.78rem; font-weight: 500; font-family: inherit;
  background: transparent; border: none; border-radius: 6px; color: var(--muted);
  cursor: pointer; transition: color .15s, background .15s;
  -webkit-tap-highlight-color: transparent; touch-action: manipulation;
}
.nav-btn:hover { color: var(--text); background: var(--surface2); }
.nav-btn.active { color: #fff; background: var(--accent); }

.view { display: none; }
.view.active { display: block; animation: fadeIn .2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* —— KPI —— */
.kpi-row {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 8px; margin-bottom: 14px;
}
.kpi {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 12px;
}
.kpi-val { font-size: 1.35rem; font-weight: 700; line-height: 1; color: #fff; }
.kpi-lbl { font-size: 0.68rem; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.03em; }

/* —— Grid layout —— */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media (max-width: 1024px) {
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .analisis-heroes-grid { grid-template-columns: 1fr; }
  .topbar-actions { margin-left: 0; width: 100%; }
  .topbar-brand h1 { font-size: 1rem; }
  .embudo-viewer { min-height: 60vh; }
  .embudo-frame { min-height: 50vh; }
}
@media (max-width: 900px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }

.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  overflow: hidden;
}
.card-head {
  padding: 10px 14px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;
}
.card-head h2 { margin: 0; font-size: 0.82rem; font-weight: 600; }
.card-head .hint { font-size: 0.7rem; color: var(--muted); }
.card-body { padding: 12px 14px; }

/* —— Flujo compacto —— */
.flujo-compact { display: flex; flex-wrap: wrap; gap: 6px; }
.flujo-pill {
  flex: 1; min-width: 140px; padding: 8px 10px; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 6px; cursor: pointer; transition: border-color .15s;
}
.flujo-pill:hover, .flujo-pill.active { border-color: var(--accent); }
.flujo-pill .step { font-size: 0.65rem; color: var(--accent); font-weight: 600; }
.flujo-pill .name { font-size: 0.78rem; font-weight: 600; margin: 2px 0; }
.flujo-pill .cnt { font-size: 1.1rem; font-weight: 700; color: var(--accent); }

/* —— Radar / hero compacto —— */
.hero-compact {
  border: 1px solid rgba(88,166,255,0.35); border-radius: var(--radius);
  background: linear-gradient(135deg, rgba(13,94,89,0.2), rgba(88,166,255,0.08));
  padding: 12px 14px;
}
.hero-compact .hero-top {
  display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px 16px; margin-bottom: 8px;
}
.hero-compact h2 { margin: 0; font-size: 0.88rem; font-weight: 600; flex: 1 1 200px; }
.hero-compact .meta { font-size: 0.7rem; color: var(--muted); }
.hero-stats {
  display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;
}
.hero-stat {
  background: rgba(0,0,0,0.25); border-radius: 6px; padding: 6px 10px; min-width: 72px;
}
.hero-stat .lbl { font-size: 0.6rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
.hero-stat .val { font-size: 0.85rem; font-weight: 600; margin-top: 1px; }
.hero-compact .resumen { font-size: 0.75rem; color: var(--muted); margin: 0 0 6px; line-height: 1.4; }
.hero-compact a { font-size: 0.72rem; color: var(--accent); text-decoration: none; }
.hero-compact a:hover { text-decoration: underline; }

/* —— Tarjetas análisis (formato radar) —— */
.analisis-hero {
  background: linear-gradient(135deg, rgba(13,94,89,0.18), rgba(88,166,255,0.07));
  border: 1px solid rgba(88,166,255,0.28); border-radius: var(--radius);
  padding: 12px 14px; min-width: 0; overflow: hidden;
}
.analisis-hero h2 {
  margin: 0 0 4px; font-size: 0.85rem; font-weight: 600;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.analisis-hero .meta { font-size: 0.68rem; color: var(--muted); margin-bottom: 8px; }
.analisis-stat {
  background: rgba(0,0,0,0.22); border-radius: 6px; padding: 6px 8px; min-width: 0;
}
.analisis-stat.stat-tema { margin-bottom: 6px; }
.analisis-stat .lbl { font-size: 0.58rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
.analisis-stat .val {
  font-size: 0.78rem; font-weight: 600; margin-top: 2px; line-height: 1.35;
  word-break: break-word; overflow-wrap: anywhere;
}
.analisis-stat.stat-tema .val {
  font-size: 0.72rem; font-weight: 500;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.analisis-hero-grid {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px; margin-bottom: 8px;
}
@media (max-width: 480px) { .analisis-hero-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.analisis-resumen {
  font-size: 0.72rem; color: var(--muted); line-height: 1.4; margin: 0 0 6px;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.analisis-hero a.informe-link { font-size: 0.7rem; color: var(--accent); text-decoration: none; }
.analisis-hero a.informe-link:hover { text-decoration: underline; }
.analisis-heroes-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 10px;
}

/* —— Capas —— */
.capa-block { margin-bottom: 16px; }
.capa-label {
  display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
  padding-left: 10px; border-left: 3px solid var(--accent);
}
.capa-label.producto { border-left-color: var(--purple); }
.capa-label h3 { margin: 0; font-size: 0.82rem; font-weight: 600; }
.capa-label span { font-size: 0.7rem; color: var(--muted); }

/* —— Tablas —— */
.tbl { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.tbl th {
  text-align: left; padding: 7px 10px; font-weight: 500; color: var(--muted);
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border); background: var(--surface2);
  position: sticky; top: 0;
}
.tbl td { padding: 8px 10px; border-bottom: 1px solid rgba(48,54,61,0.6); vertical-align: middle; }
.tbl tr:hover td { background: rgba(88,166,255,0.04); }
.tbl tr.expandable { cursor: pointer; }
.tbl .detail-row td { background: var(--surface2); font-size: 0.72rem; color: var(--muted); padding: 8px 10px 10px; }
.tbl code { font-size: 0.68rem; color: var(--muted); }
.tbl-wrap { overflow-x: auto; max-height: 520px; overflow-y: auto; }

.badge {
  display: inline-block; padding: 2px 7px; font-size: 0.65rem; font-weight: 600;
  border-radius: 4px; text-transform: uppercase; letter-spacing: 0.02em;
}
.badge.live { background: rgba(63,185,80,0.15); color: var(--green); }
.badge.mock { background: rgba(139,148,158,0.15); color: var(--muted); }
.badge.viable { background: rgba(63,185,80,0.15); color: var(--green); }
.badge.condicional { background: rgba(210,153,34,0.15); color: var(--yellow); }
.badge.hecho { background: rgba(63,185,80,0.15); color: var(--green); }
.badge.parcial { background: rgba(210,153,34,0.15); color: var(--yellow); }
.badge.falta { background: rgba(248,81,73,0.15); color: var(--red); }

.bar-mini { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; width: 60px; display: inline-block; vertical-align: middle; }
.bar-mini-fill { height: 100%; background: var(--accent); border-radius: 2px; }

.chart-box { height: 180px; position: relative; }

.subnav { display: flex; gap: 4px; margin-bottom: 10px; flex-wrap: wrap; }
.subnav button {
  padding: 5px 10px; font-size: 0.72rem; font-family: inherit; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 5px; color: var(--muted); cursor: pointer;
}
.subnav button.active { color: #fff; border-color: var(--accent); background: rgba(88,166,255,0.15); }
.subpanel { display: none; }
.subpanel.active { display: block; }

.embudo-mini { display: grid; gap: 6px; }
.embudo-mini-row {
  display: grid; grid-template-columns: 24px 1fr 36px; gap: 8px; align-items: center; font-size: 0.75rem;
}
.embudo-mini-bar { height: 5px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
.embudo-mini-fill { height: 100%; background: var(--accent); border-radius: 3px; }
.embudo-mini-foot { margin: 8px 0 0; font-size: 0.72rem; }

.embudo-intro {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px;
  margin-bottom: 12px; font-size: 0.78rem; color: var(--muted);
}
.embudo-intro p { margin: 0; flex: 1; min-width: 200px; }
.btn-outline {
  display: inline-block; font-size: 0.72rem; color: var(--accent); text-decoration: none;
  padding: 5px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface2);
  font-family: inherit; cursor: pointer;
}
.btn-outline:hover { border-color: var(--accent); }
.embudo-step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 50%; background: var(--accent); color: #fff;
  font-size: 0.72rem; font-weight: 700; margin-bottom: 6px;
}
.embudo-step h3 { margin: 0 0 4px; font-size: 0.82rem; font-weight: 600; }
.embudo-step p { margin: 0 0 8px; font-size: 0.72rem; color: var(--muted); line-height: 1.35; }
.embudo-step-meta { font-size: 0.65rem; }
.embudo-pendientes { margin: 0; padding-left: 18px; font-size: 0.75rem; color: var(--muted); }
.embudo-pendientes li { margin-bottom: 4px; }
.prod-plan { display: grid; gap: 10px; }
.prod-paso {
  background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 12px 14px;
}
.prod-paso.done { border-color: rgba(63,185,80,0.35); }
.prod-paso-head {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px;
}
.prod-paso-head h3 { margin: 0; font-size: 0.82rem; font-weight: 600; flex: 1; }
.prod-paso-progress { font-size: 0.68rem; color: var(--muted); }
.prod-meta { font-size: 0.72rem; color: var(--muted); margin-bottom: 8px; line-height: 1.45; }
.prod-meta strong { color: var(--text); font-weight: 600; }
.prod-apps { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; }
.prod-app {
  font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;
  background: rgba(88,166,255,0.12); color: var(--accent); border: 1px solid rgba(88,166,255,0.25);
}
.prod-checklist { list-style: none; margin: 0; padding: 0; }
.prod-checklist li { margin-bottom: 6px; }
.prod-check {
  display: flex; align-items: flex-start; gap: 10px; font-size: 0.75rem; color: var(--text);
  cursor: pointer; -webkit-tap-highlight-color: transparent; touch-action: manipulation;
}
.prod-check input {
  width: 18px; height: 18px; min-width: 18px; margin-top: 1px; accent-color: var(--accent); cursor: pointer;
}
.prod-check.done span { color: var(--muted); text-decoration: line-through; }
.prod-intro { font-size: 0.75rem; color: var(--muted); margin: 0 0 12px; line-height: 1.45; }
.embudo-steps {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;
}
.embudo-step {
  display: block; text-align: left; width: 100%; font-family: inherit;
  text-decoration: none; color: inherit; cursor: pointer;
  background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 12px 14px; transition: border-color 0.15s;
}
.embudo-step:hover { border-color: var(--accent); }
.embudo-step.step-done { border-color: rgba(63,185,80,0.35); }
.embudo-flow {
  display: flex; align-items: center; flex-wrap: wrap; gap: 4px 6px;
  margin-bottom: 12px; font-size: 0.72rem; color: var(--muted);
}
.embudo-flow-item {
  width: 26px; height: 26px; border-radius: 50%; display: inline-flex;
  align-items: center; justify-content: center; font-weight: 700;
  border: 1px solid var(--border); background: var(--surface2); color: var(--muted);
}
.embudo-flow-item.done { border-color: rgba(63,185,80,0.4); color: var(--green); }
.embudo-flow-arrow { color: var(--border); user-select: none; }
.embudo-viewer { display: flex; flex-direction: column; gap: 8px; min-height: 520px; }
.embudo-viewer[hidden] { display: none !important; }
#embudo-overview[hidden] { display: none !important; }
.embudo-toolbar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px;
  padding: 10px 12px; background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius);
  position: sticky; top: 0; z-index: 20;
}
.embudo-viewer-title { flex: 1; font-size: 0.82rem; font-weight: 600; min-width: 120px; }
.embudo-viewer-step { font-size: 0.68rem; color: var(--muted); margin-left: 4px; }
.embudo-tool-group { display: flex; flex-wrap: wrap; gap: 8px; margin-left: auto; width: 100%; }
@media (min-width: 640px) { .embudo-tool-group { width: auto; margin-left: auto; } }
.embudo-tool {
  font-family: inherit; font-size: 0.78rem; font-weight: 500; color: var(--accent);
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 14px; min-height: 44px; cursor: pointer;
  -webkit-tap-highlight-color: transparent; touch-action: manipulation;
}
.embudo-tool:hover:not(:disabled):not(.is-disabled) { border-color: var(--accent); background: var(--bg); }
.embudo-tool:disabled, .embudo-tool.is-disabled { opacity: 0.35; cursor: default; pointer-events: none; }
.embudo-tool-link { text-decoration: none; display: inline-flex; align-items: center; }
.embudo-frame {
  flex: 1; width: 100%; min-height: 480px; border: 1px solid var(--border);
  border-radius: var(--radius); background: #fff;
}

.rent-top3 {
  background: rgba(63,185,80,0.08); border: 1px solid rgba(63,185,80,0.25);
  border-radius: var(--radius); padding: 10px 14px; margin-bottom: 12px;
}
.rent-top3 h2 { margin: 0 0 6px; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--green); }
.rent-top3 ol { margin: 0; padding-left: 18px; font-size: 0.78rem; }
.rent-leyenda {
  display: flex; flex-wrap: wrap; gap: 8px 14px; font-size: 0.68rem; color: var(--muted); margin-bottom: 12px;
}
.rent-leyenda span { display: flex; align-items: center; gap: 5px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-alta { background: var(--green); }
.dot-media { background: var(--yellow); }
.dot-baja { background: var(--red); }
.dot-no { background: var(--muted); }
.rent-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px;
}
.rent-card {
  background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 12px 14px; min-width: 0;
}
.rent-card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px; }
.rent-rank { font-size: 0.68rem; font-weight: 700; color: var(--muted); }
.rent-badge {
  font-size: 0.62rem; font-weight: 700; padding: 2px 7px; border-radius: 999px; white-space: nowrap;
}
.rent-alta { background: rgba(63,185,80,0.15); color: var(--green); }
.rent-media { background: rgba(210,153,34,0.15); color: var(--yellow); }
.rent-baja { background: rgba(248,81,73,0.15); color: var(--red); }
.rent-no { background: rgba(139,148,158,0.15); color: var(--muted); }
.rent-card h3 { margin: 0 0 6px; font-size: 0.82rem; font-weight: 600; line-height: 1.35; }
.rent-why { margin: 0 0 8px; font-size: 0.72rem; color: var(--muted); line-height: 1.4; }
.rent-meta { font-size: 0.68rem; color: var(--muted); }
.estado-tag { font-size: 0.65rem; }
.estado-tag.listo { color: var(--green); }
.estado-tag.falta { color: var(--yellow); }
.rent-footer { margin: 12px 0 0; font-size: 0.68rem; color: var(--muted); text-align: center; }

.skills-row { display: flex; flex-wrap: wrap; gap: 4px; }
.skill-chip {
  font-size: 0.68rem; padding: 3px 8px; border: 1px solid var(--border);
  border-radius: 4px; color: var(--muted);
}

.footer {
  margin-top: 20px; padding-top: 12px; border-top: 1px solid var(--border);
  font-size: 0.7rem; color: var(--muted); text-align: center;
}
.empty { color: var(--muted); font-size: 0.78rem; padding: 12px 0; margin: 0; }
"""

HUD_JS = """
const ACCENT = '#58a6ff';
const FONT = { family: 'Inter', size: 11 };

function initCharts(D) {
  if (typeof Chart === 'undefined') {
    document.querySelectorAll('.chart-box').forEach(el => {
      el.innerHTML = '<p class="empty">Gráficos no disponibles sin conexión a internet.</p>';
    });
    return;
  }
  try {
  Chart.defaults.color = '#8b949e';
  Chart.defaults.borderColor = '#30363d';
  const tip = {
    backgroundColor: '#1c2128', titleColor: '#e6edf3', bodyColor: '#8b949e',
    borderColor: ACCENT, borderWidth: 1, padding: 8,
  };

  const mk = (id, cfg) => {
    const el = document.getElementById(id);
    if (el) new Chart(el, cfg);
  };

  mk('chartCola', {
    type: 'doughnut',
    data: {
      labels: D.cola_labels,
      datasets: [{ data: D.cola_values, backgroundColor: ['#58a6ff','#3fb950','#d29922','#a371f7','#f85149'], borderWidth: 0 }],
    },
    options: { responsive: true, maintainAspectRatio: false, cutout: '62%',
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 8, padding: 8, font: FONT } }, tooltip: tip } },
  });

  mk('chartModulos', {
    type: 'doughnut',
    data: {
      labels: D.modulos_chart_labels,
      datasets: [{ data: D.modulos_chart_values, backgroundColor: ['#3fb950','#d29922','#f85149'], borderWidth: 0 }],
    },
    options: { responsive: true, maintainAspectRatio: false, cutout: '62%',
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 8, font: FONT } }, tooltip: tip } },
  });

  mk('chartProd', {
    type: 'bar',
    data: {
      labels: D.produccion_labels,
      datasets: [{ data: D.produccion_values, backgroundColor: 'rgba(88,166,255,0.4)', borderColor: ACCENT, borderWidth: 1, borderRadius: 3 }],
    },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: tip },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1, font: FONT }, grid: { color: 'rgba(255,255,255,0.04)' } },
        x: { ticks: { font: FONT, maxRotation: 30 }, grid: { display: false } },
      },
    },
  });
  } catch (e) {
    console.warn('Charts no disponibles', e);
  }
}

function showView(v) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.view === v));
  document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === 'view-' + v));
  if (v !== 'embudo') resetEmbudoOverview();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetEmbudoOverview() {
  const overview = document.getElementById('embudo-overview');
  const viewer = document.getElementById('embudo-viewer');
  const frame = document.getElementById('embudo-frame');
  if (!overview || !viewer) return;
  overview.hidden = false;
  viewer.hidden = true;
  if (frame) frame.src = 'about:blank';
}

function setEmbudoBtn(btn, enabled) {
  if (!btn) return;
  btn.disabled = !enabled;
  btn.classList.toggle('is-disabled', !enabled);
  btn.setAttribute('aria-disabled', String(!enabled));
}

function initEmbudo() {
  const shell = document.getElementById('embudo-shell');
  if (!shell) return;
  const overview = document.getElementById('embudo-overview');
  const viewer = document.getElementById('embudo-viewer');
  const frame = document.getElementById('embudo-frame');
  const titleEl = document.getElementById('embudo-viewer-title');
  const stepEl = document.getElementById('embudo-viewer-step');
  const ext = document.getElementById('embudo-external');
  const btnPrev = document.querySelector('[data-embudo-prev]');
  const btnNext = document.querySelector('[data-embudo-next]');
  const indexUrl = shell.dataset.indexUrl || '';
  let steps = [];
  try { steps = JSON.parse(shell.dataset.steps || '[]'); } catch (_) { steps = []; }
  steps.sort((a, b) => a.paso - b.paso);
  let current = null;

  function pasoFromHref(href) {
    const h = (href || '').toLowerCase();
    if (!h || h.startsWith('http') || h.startsWith('mailto') || h.startsWith('tel') || h.startsWith('#')) return null;
    if (h.includes('index.html') && !/paso-\\d/.test(h)) return 0;
    const m = h.match(/paso-(\\d+)/);
    return m ? parseInt(m[1], 10) : null;
  }

  function itemForPaso(paso) {
    if (paso === 0) return { url: indexUrl, title: 'Índice del embudo', paso: 0 };
    return steps.find(s => s.paso === paso) || null;
  }

  function itemFromHref(href) {
    const paso = pasoFromHref(href);
    return paso === null ? null : itemForPaso(paso);
  }

  function updateToolbar(paso) {
    if (stepEl) {
      stepEl.textContent = paso > 0 ? `Paso ${paso} de ${steps.length}` : 'Índice';
    }
    setEmbudoBtn(btnPrev, paso > 0);
    setEmbudoBtn(btnNext, paso < steps.length);
  }

  function openItem(item) {
    if (!item?.url || !frame) return;
    overview.hidden = true;
    viewer.hidden = false;
    frame.src = item.url;
    if (titleEl) titleEl.textContent = item.title || 'Embudo';
    if (ext) ext.href = item.url;
    current = item;
    updateToolbar(item.paso || 0);
  }

  function syncFromFrame() {
    if (!frame) return;
    try {
      const path = frame.contentWindow.location.pathname + frame.contentWindow.location.search;
      const paso = pasoFromHref(path);
      if (paso === null) return;
      const item = itemForPaso(paso);
      if (!item) return;
      current = item;
      if (titleEl) titleEl.textContent = item.title || 'Embudo';
      if (ext) ext.href = item.url;
      updateToolbar(paso);
    } catch (_) {}
  }

  function hijackIframeNav() {
    if (!frame) return;
    try {
      const doc = frame.contentDocument;
      if (!doc) return;
      doc.querySelectorAll('.embudo-inline-nav').forEach(el => { el.hidden = true; });
      doc.querySelectorAll('a[href]').forEach(a => {
        const href = a.getAttribute('href') || '';
        const paso = pasoFromHref(href);
        if (paso === null) return;
        if (a.dataset.embudoBound === '1') return;
        a.dataset.embudoBound = '1';
        a.addEventListener('click', (e) => {
          e.preventDefault();
          const item = itemFromHref(href);
          if (item) openItem(item);
        });
      });
    } catch (_) {}
  }

  shell.querySelectorAll('[data-embudo-url]').forEach(el => {
    el.addEventListener('click', () => openItem({
      url: el.dataset.embudoUrl,
      title: el.dataset.embudoTitle || 'Embudo',
      paso: parseInt(el.dataset.embudoPaso || '0', 10),
    }));
  });

  document.querySelector('[data-embudo-back]')?.addEventListener('click', resetEmbudoOverview);

  btnPrev?.addEventListener('click', () => {
    if (!current) {
      if (indexUrl) openItem({ url: indexUrl, title: 'Índice del embudo', paso: 0 });
      return;
    }
    if (current.paso <= 1) {
      if (indexUrl) openItem({ url: indexUrl, title: 'Índice del embudo', paso: 0 });
      return;
    }
    const prev = steps.find(s => s.paso === current.paso - 1);
    if (prev) openItem(prev);
  });

  btnNext?.addEventListener('click', () => {
    if (!current) {
      if (steps.length) openItem(steps[0]);
      return;
    }
    if (current.paso === 0 && steps.length) {
      openItem(steps[0]);
      return;
    }
    const next = steps.find(s => s.paso === current.paso + 1);
    if (next) openItem(next);
  });

  frame?.addEventListener('load', () => {
    syncFromFrame();
    hijackIframeNav();
  });

  window.addEventListener('message', (ev) => {
    if (!ev.data || ev.data.type !== 'embudo-nav') return;
    const item = itemFromHref(ev.data.href || '');
    if (item) openItem(item);
  });
}

function initEmbudoChecklist() {
  const root = document.getElementById('embudo-produccion');
  if (!root) return;
  const key = 'cursorprime_embudo_prod_' + (root.dataset.cliente || 'default');
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (_) { saved = {}; }

  function updatePasoProgress(pasoEl) {
    const checks = pasoEl.querySelectorAll('.prod-check input');
    const done = [...checks].filter(c => c.checked).length;
    const total = checks.length;
    const prog = pasoEl.querySelector('.prod-paso-progress');
    if (prog) prog.textContent = done + '/' + total;
    pasoEl.classList.toggle('done', total > 0 && done === total);
  }

  root.querySelectorAll('.prod-paso').forEach(pasoEl => {
    pasoEl.querySelectorAll('.prod-check input').forEach(inp => {
      const id = inp.dataset.taskId;
      if (id && saved[id]) inp.checked = true;
      inp.closest('.prod-check')?.classList.toggle('done', inp.checked);
      inp.addEventListener('change', () => {
        if (id) saved[id] = inp.checked;
        localStorage.setItem(key, JSON.stringify(saved));
        inp.closest('.prod-check')?.classList.toggle('done', inp.checked);
        updatePasoProgress(pasoEl);
      });
    });
    updatePasoProgress(pasoEl);
  });
}

function initNav() {
  document.querySelectorAll('.nav-btn, .quick-btn, .link-btn[data-view]').forEach(btn => {
    btn.addEventListener('click', () => {
      const v = btn.dataset.view;
      if (v) showView(v);
    });
  });
}

function initSubnav(containerId) {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.querySelectorAll('.subnav button').forEach(btn => {
    btn.addEventListener('click', () => {
      const t = btn.dataset.sub;
      c.querySelectorAll('.subnav button').forEach(b => b.classList.toggle('active', b.dataset.sub === t));
      c.querySelectorAll('.subpanel').forEach(p => p.classList.toggle('active', p.id === containerId + '-' + t));
    });
  });
}

function initFlujo() {
  document.querySelectorAll('.flujo-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const v = pill.dataset.goto;
      if (v) {
        showView(v);
        if (pill.dataset.sub) {
          const sub = pill.dataset.sub;
          setTimeout(() => {
            const op = document.getElementById('view-operaciones');
            op?.querySelector(`.subnav button[data-sub="${sub}"]`)?.click();
          }, 50);
        }
      }
    });
  });
}

function initExpandRows() {
  document.querySelectorAll('.tbl tr.expandable').forEach(row => {
    row.addEventListener('click', () => {
      const next = row.nextElementSibling;
      if (next && next.classList.contains('detail-row')) {
        next.style.display = next.style.display === 'table-row' ? 'none' : 'table-row';
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const D = window.INVENTARIO;
  initCharts(D);
  initNav();
  initEmbudo();
  initEmbudoChecklist();
  initSubnav('operaciones');
  initFlujo();
  initExpandRows();
});
"""

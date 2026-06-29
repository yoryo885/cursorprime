"""Genera dashboard.canvas.tsx — versión clara con explicaciones."""

from __future__ import annotations

import json

from src.panel_data import prepare_panel_data


def render_canvas(inv: dict) -> str:
    d = prepare_panel_data(inv)
    data_json = json.dumps(d, ensure_ascii=False)

    return f'''/** Centro de control prime — panel claro */
import {{ useState }} from "react";

const D = {data_json};

const panel: React.CSSProperties = {{
  background: "#121828", border: "1px solid rgba(56,189,248,0.2)", borderRadius: 12, padding: 16,
}};
const muted = {{ color: "#94a3b8", fontSize: "0.85rem" }};

export default function Dashboard() {{
  const [tab, setTab] = useState("analisis");
  const {{ metricas, flujo, avance, avance_explicacion, generado_legible, tabs_ayuda,
    analisis, implementadas, en_espera, pendientes, evaluaciones, contenido, skills_instaladas }} = D;

  const lists: Record<string, Record<string, unknown>[]> = {{
    analisis, implementadas, espera: en_espera, pendientes, evaluaciones, contenido,
    skills: skills_instaladas.map((s: string) => ({{ titulo: s }})),
  }};

  const tabLabels: [string, string][] = [
    ["analisis", "Investigaciones"], ["implementadas", "Ya hechas"], ["espera", "Pospuestas"],
    ["pendientes", "Sin revisar"], ["evaluaciones", "Evaluaciones"], ["contenido", "Contenido"], ["skills", "Skills"],
  ];

  return (
    <div style={{{{ fontFamily: "Inter, system-ui", padding: 20, color: "#e2e8f0", background: "#0a0e1a", minHeight: "100vh" }}}}>
      <h1 style={{{{ margin: "0 0 4px", fontSize: "1.4rem" }}}}>Centro de control prime</h1>
      <p style={{{{ ...muted, margin: "0 0 16px" }}}}>Actualizado {{generado_legible}}</p>

      <div style={{{{ ...panel, marginBottom: 16, background: "rgba(56,189,248,0.06)" }}}}>
        <strong style={{{{ color: "#38bdf8" }}}}>¿Qué es esto?</strong>
        <p style={{{{ margin: "8px 0 0", fontSize: "0.9rem", lineHeight: 1.5 }}}}>
          Resumen de todo lo creado en cursorprime. Solo lectura — no modifica tus proyectos.
        </p>
      </div>

      <div style={{{{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 16 }}}}>
        {{flujo.map((p: Record<string, unknown>) => (
          <div key={{String(p.paso)}} style={{{{ ...panel, flex: "1 1 180px", cursor: "pointer" }}}}
            onClick={{() => setTab(["analisis","pendientes","evaluaciones","contenido"][Number(p.paso)-1] || "analisis")}}>
            <div style={{{{ fontSize: "0.75rem", color: "#38bdf8" }}}}>Paso {{String(p.paso)}}</div>
            <div style={{{{ fontWeight: 600, marginBottom: 4 }}}}>{{String(p.nombre_corto || p.nombre)}}</div>
            <div style={{{{ fontSize: "1.4rem", fontWeight: 700, color: "#fff" }}}}>{{String(p.count)}}</div>
          </div>
        ))}}
      </div>

      <div style={{{{ ...panel, marginBottom: 16, display: "flex", gap: 16, alignItems: "center" }}}}>
        <div style={{{{ fontSize: "2rem", fontWeight: 700, color: "#4ade80" }}}}>{{avance}}%</div>
        <div>
          <div style={{{{ fontWeight: 600 }}}}>Avance de la cola</div>
          <div style={{{{ ...muted }}}}>{{avance_explicacion}}</div>
        </div>
      </div>

      <div style={{{{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10, marginBottom: 16 }}}}>
        {{metricas.map((m: Record<string, unknown>) => (
          <div key={{String(m.id)}} style={{panel}}>
            <div style={{{{ fontSize: "1.5rem", fontWeight: 700 }}}}>{{String(m.valor)}}</div>
            <div style={{{{ fontSize: "0.82rem", fontWeight: 600, margin: "4px 0" }}}}>{{String(m.titulo)}}</div>
            <div style={{{{ fontSize: "0.72rem", color: "#94a3b8" }}}}>{{String(m.explicacion)}}</div>
          </div>
        ))}}
      </div>

      <div style={{panel}}>
        <p style={{{{ ...muted, margin: "0 0 12px" }}}}>{{tabs_ayuda[tab]}}</p>
        <div style={{{{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}}}>
          {{tabLabels.map(([id, label]) => (
            <button key={{id}} onClick={{() => setTab(id)}} style={{{{
              padding: "6px 12px", fontSize: "0.8rem", borderRadius: 8, cursor: "pointer",
              border: tab === id ? "1px solid #38bdf8" : "1px solid rgba(255,255,255,0.1)",
              background: tab === id ? "rgba(56,189,248,0.12)" : "transparent",
              color: tab === id ? "#fff" : "#94a3b8",
            }}}}>{{label}}</button>
          ))}}
        </div>
        <ul style={{{{ margin: 0, paddingLeft: 18, fontSize: "0.88rem", lineHeight: 1.7 }}}}>
          {{(lists[tab] || []).slice(0, 15).map((item, i) => (
            <li key={{i}}>{{String(item.titulo || item.tema || item.slug || "—")}}</li>
          ))}}
          {{!(lists[tab] || []).length && <li style={{{{ ...muted }}}}>Nada aquí todavía.</li>}}
        </ul>
      </div>
    </div>
  );
}}
'''

"""Plantillas HTML/CSS y conversión a PDF con Playwright."""
from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.agents.book_package import BookPackage, TopicTable
    from src.models import TopicResult

CATEGORY_COLORS = [
    {"bg": "#0F6E56", "light": "#1D9E75", "text": "#E1F5EE"},
    {"bg": "#534AB7", "light": "#7F77DD", "text": "#EEEDFE"},
    {"bg": "#993C1D", "light": "#D85A30", "text": "#FAECE7"},
    {"bg": "#993556", "light": "#D4537E", "text": "#FBEAF0"},
    {"bg": "#085041", "light": "#5DCAA5", "text": "#E1F5EE"},
    {"bg": "#3C3489", "light": "#AFA9EC", "text": "#EEEDFE"},
]

EDITORIAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;0,7..72,700;1,7..72,400&family=Source+Sans+3:wght@400;600&display=swap');

:root {
  --ink: #1a1a1a;
  --muted: #5c6b65;
  --accent: #4caf7d;
  --accent-emphasis: #1f6b47;
  --accent-label: #3a9670;
  --accent-light: #e8f8ef;
  --green-card-bg: #e8f5e9;
  --green-card-border: #4caf50;
  --border: #d8e4de;
  --paper: #f9faf8;
  --cover-bg: #0a0a0a;
  --cover-ink: #ffffff;
  --cover-muted: rgba(255, 255, 255, 0.55);
  --serif: 'Literata', Georgia, 'Palatino Linotype', 'Book Antiqua', serif;
  --sans: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
}

@page {
  size: A4;
  margin: 18mm 20mm 22mm 20mm;
}

@page action-plan {
  size: A4;
  margin: 10mm 11mm 10mm 11mm;
}

@page :first {
  margin: 0;
  size: A4;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

* {
  hyphens: none !important;
  -webkit-hyphens: none !important;
}

body {
  font-family: var(--serif);
  font-size: 11pt;
  line-height: 1.55;
  color: var(--ink);
  background: white;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.page-break { page-break-after: always; }
.avoid-break {
  page-break-inside: avoid;
  break-inside: avoid-page;
}

/* Tarjetas editoriales: cada tarjeta entera; si no caben las 3 juntas, la aplicación pasa sola a la página siguiente */
.topic-tables {
  margin-top: 1rem;
  padding-top: 0.25rem;
  page-break-inside: auto;
  break-inside: auto;
}

.tbl-editorial-cards .tbl-editorial-card,
.tbl-editorial-card {
  page-break-inside: avoid;
  break-inside: avoid-page;
  -webkit-column-break-inside: avoid;
}

.tbl-editorial-card--aplicacion {
  page-break-before: auto;
  break-before: auto;
}

.table-page-icons.page-icons {
  page-break-inside: auto;
  break-inside: auto;
}

/* —— Portada (estilo 33.pdf: posiciones absolutas, label arriba-izq) —— */
.cover {
  background: var(--cover-bg);
  color: var(--cover-ink);
  position: relative;
  width: 210mm;
  min-height: 297mm;
  height: 297mm;
  margin: 0;
  padding: 0;
  page-break-after: always;
  box-sizing: border-box;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.cover-top {
  margin: 0;
  padding: 0;
}

.cover-label {
  position: absolute;
  top: 72px;
  left: 43px;
  font-family: var(--sans);
  font-size: 10.5pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0;
}

.cover-hero {
  margin: 0;
  line-height: 1;
  font-family: var(--sans);
  font-weight: 700;
  letter-spacing: -0.04em;
}

.cover-hero-80 {
  position: absolute;
  top: 533px;
  left: 84px;
  display: block;
  font-size: 172pt;
  line-height: 1;
  color: var(--cover-ink);
  margin: 0;
  z-index: 3;
}

.cover-hero-20 {
  position: absolute;
  top: 727px;
  left: 80px;
  display: block;
  font-size: 172pt;
  line-height: 1;
  color: var(--accent);
  margin: 0;
  z-index: 3;
}

.cover-title {
  position: absolute;
  top: 973px;
  left: 74px;
  font-family: var(--sans);
  font-size: 19pt;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.12;
  margin: 0;
  max-width: 16cm;
  color: var(--cover-ink);
}

.cover-subtitle {
  position: absolute;
  top: 266mm;
  left: 20.4mm;
  font-family: var(--sans);
  font-size: 10.5pt;
  font-weight: 500;
  color: var(--cover-muted);
  margin: 0;
  max-width: 16cm;
  line-height: 1.3;
}

.cover-author {
  position: absolute;
  top: 272mm;
  left: 20.4mm;
  font-family: var(--sans);
  font-size: 11.5pt;
  font-weight: 400;
  color: var(--cover-muted);
  margin: 0;
}

.cover-bottom {
  position: absolute;
  top: 284.7mm;
  left: 16.7mm;
  right: 20mm;
  width: auto;
  padding-top: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.cover-meta {
  position: absolute;
  left: 76px;
  top: 1072px;
  font-family: var(--sans);
  font-size: 8.5pt;
  color: var(--cover-muted);
  line-height: 1.5;
}

.cover-dot {
  position: absolute;
  left: 705px;
  top: 1071px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--accent);
}

.cover-photo-wrap {
  position: absolute;
  top: 115px;
  left: -14px;
  right: 0;
  height: calc(256.1mm - 115px);
  overflow: hidden;
  border-radius: 0 12px 12px 0;
  border: 2px solid var(--accent);
  border-left: none;
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.cover-photo-wrap img {
  position: absolute;
  left: -100px;
  top: -4px;
  width: 118%;
  height: calc(100% + 8px);
  object-fit: cover;
  object-position: 74% 26%;
  display: block;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* —— Perfil del lector (página 2: el autor) —— */
.perfil-lector {
  page-break-before: always;
  page-break-after: always;
  padding: 3rem 0 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 60%;
}
.perfil-rule {
  width: 42px;
  height: 4px;
  background: var(--accent);
  margin-bottom: 1.5rem;
}
.perfil-titulo {
  font-family: var(--sans);
  font-size: 8pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent-label);
  font-weight: 600;
  margin-bottom: 0.35rem;
}
.perfil-nombre {
  font-family: var(--serif);
  font-size: 18pt;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 1.5rem;
}
.perfil-intro {
  font-family: var(--serif);
  font-size: 11pt;
  font-style: normal;
  color: #3d4a44;
  max-width: 92%;
  border-left: 3px solid var(--accent);
  padding-left: 1.25rem;
  padding-top: 0.2rem;
  padding-bottom: 0.2rem;
  line-height: 1.55;
  margin-bottom: 2rem;
}
.perfil-audiencia {
  font-family: var(--serif);
  font-size: 10.5pt;
  line-height: 1.6;
  color: #2a3d34;
  max-width: 92%;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
  padding-left: 1.25rem;
  border-left: 3px solid var(--accent-light);
}

.audiencia-aviso {
  max-width: 92%;
  margin-top: 1.75rem;
  padding: 1.1rem 1.25rem;
  background: #eef6f0;
  border: 2px solid #2a5c45;
  border-radius: 4px;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.audiencia-aviso-label {
  font-family: var(--sans);
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #2a5c45;
  margin-bottom: 0.45rem;
}

.audiencia-aviso-text {
  font-family: var(--sans);
  font-size: 10.5pt;
  font-weight: 600;
  color: #1a3d2e;
  line-height: 1.5;
  margin: 0;
}

/* —— Página para quién (página 3: audiencia) —— */
.audiencia-page {
  page-break-before: always;
  page-break-after: always;
  padding: 3rem 0 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: auto;
}
.audiencia-page .perfil-valor {
  font-family: var(--serif);
  font-size: 16pt;
  font-weight: 600;
  color: var(--ink);
}
.perfil-items {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.perfil-item {
  border-left: 3px solid var(--accent);
  padding-left: 1.25rem;
}
.perfil-label {
  font-family: var(--sans);
  font-size: 7.5pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  opacity: 0.7;
  margin-bottom: 0.35rem;
}
.perfil-valor {
  font-family: var(--serif);
  font-size: 12pt;
  line-height: 1.5;
  color: #2a332f;
}

/* —— Mapa conceptual —— */
.map-section {
  page-break-after: always;
  padding-top: 0.5rem;
}

.section-kicker {
  font-family: var(--sans);
  font-size: 8pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.section-title {
  font-size: 20pt;
  font-weight: 700;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

.mindmap-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.75rem;
  margin-bottom: 1.5rem;
}

.mindmap-center {
  text-align: center;
  background: #37474F;
  color: white;
  border-radius: 50%;
  width: 150px;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  font-family: var(--sans);
  font-size: 9pt;
  font-weight: 700;
  line-height: 1.3;
  box-shadow: 0 4px 18px rgba(55, 71, 79, 0.22);
  page-break-inside: avoid;
}

.mindmap-center-icon {
  font-size: 22px;
  margin-bottom: 0.35rem;
  line-height: 1;
}

.mindmap-branches {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
  gap: 1rem;
  width: 100%;
}

.mindmap-branch {
  border-radius: 18px;
  padding: 1rem 1.1rem;
  border: 2px solid color-mix(in srgb, var(--branch-color, var(--accent)) 40%, white);
  background: color-mix(in srgb, var(--branch-color, var(--accent)) 10%, white);
  page-break-inside: avoid;
  box-shadow: 0 2px 10px rgba(55, 71, 79, 0.07);
}

.mindmap-branch-title {
  font-family: var(--sans);
  font-size: 8.5pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.65rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: var(--branch-color, var(--accent));
  color: white;
  display: inline-block;
}

.mindmap-nodes {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.mindmap-node {
  font-size: 9pt;
  line-height: 1.45;
  padding: 0.4rem 0.55rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.82);
  border-left: 3px solid var(--branch-color, var(--accent));
}

.mindmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.category-card {
  border-radius: 18px;
  padding: 1rem 1.1rem;
  border: 2px solid color-mix(in srgb, var(--cat-color, var(--accent)) 35%, white);
  background: color-mix(in srgb, var(--cat-color, var(--accent)) 8%, white);
  page-break-inside: avoid;
  box-shadow: 0 2px 10px rgba(55, 71, 79, 0.06);
}

.category-card h3 {
  font-family: var(--sans);
  font-size: 8.5pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.6rem;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  background: var(--cat-color, var(--accent));
  color: white;
  display: inline-block;
}

.category-card ul {
  list-style: none;
  font-size: 9pt;
  line-height: 1.5;
  margin-top: 0.5rem;
}

.category-card li {
  padding: 0.35rem 0.5rem;
  margin-bottom: 0.25rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.75);
  border: none;
}

.category-card li:last-child { margin-bottom: 0; }

.connections {
  margin-top: 0.5rem;
}

.connections h3 {
  font-family: var(--sans);
  font-size: 9pt;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin-bottom: 0.6rem;
}

.conn-list {
  list-style: none;
  font-size: 9pt;
}

.conn-list li {
  padding: 0.35rem 0;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.5rem;
  align-items: baseline;
}

.conn-from, .conn-to {
  font-weight: 600;
  color: var(--accent);
}

.conn-arrow { color: var(--muted); }

.conn-label {
  flex: 1 1 100%;
  font-style: italic;
  color: var(--muted);
  font-size: 8.5pt;
  padding-left: 0.5rem;
}

/* —— Página de tema (solo resumen) —— */
.topic {
  page-break-before: always;
  padding-top: 0.25rem;
}

.topic-header {
  margin-bottom: 1.25rem;
  padding-bottom: 0.85rem;
  border-bottom: 2px solid var(--accent);
  page-break-after: avoid;
  break-after: avoid-page;
}

.topic-number {
  font-family: var(--sans);
  font-size: 8pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.topic-title {
  font-family: var(--serif);
  font-size: 20pt;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.15;
  color: var(--ink);
  margin-bottom: 0.3rem;
}

.topic-voice {
  font-family: var(--sans);
  font-size: 8.5pt;
  color: var(--accent);
}

.summary {
  text-align: justify;
}

.summary p {
  font-family: var(--serif);
  font-size: 10.5pt;
  line-height: 1.6;
  color: #222;
  margin-bottom: 0.85rem;
}

.summary p:last-child { margin-bottom: 0; }

/* —— Página de tabla (imagen Playwright, página aparte) —— */
.table-page {
  page-break-before: always;
  padding: 1.5rem 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.table-page img {
  width: 100%;
  max-width: 680px;
  height: auto;
}

/* —— Tabla —— */
.concept-table-wrap {
  margin-top: 0.5rem;
  page-break-inside: avoid;
}

.concept-table-label {
  font-family: var(--sans);
  font-size: 8.5pt;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent);
  margin-bottom: 0.5rem;
}

.concept-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  line-height: 1.45;
}

.concept-table thead th {
  font-family: var(--sans);
  font-weight: 600;
  text-align: left;
  padding: 0.55rem 0.65rem;
  background: var(--accent);
  color: white;
  font-size: 8.5pt;
  letter-spacing: 0.04em;
}

.concept-table tbody td {
  padding: 0.6rem 0.65rem;
  border: 1px solid var(--border);
  vertical-align: top;
  background: white;
}

.concept-table tbody tr:nth-child(even) td {
  background: var(--paper);
}

/* —— Tabla standalone (archivo individual) —— */
.standalone-table-page {
  padding: 1.5rem;
  max-width: 18cm;
  margin: 0 auto;
}

.standalone-table-page h1 {
  font-size: 16pt;
  margin-bottom: 1rem;
  color: var(--accent);
}

/* —— Base editorial (estilo tarjetas compartido) —— */
.page-table {
  background: #ffffff;
  min-height: 100vh;
}
.page-table .standalone-table-page {
  padding: 2.5rem 2rem;
  max-width: 680px;
  margin: 0 auto;
}
.page-table .standalone-table-page h1 {
  font-family: var(--serif);
  font-size: 22pt;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
  margin-bottom: 0.35rem;
  letter-spacing: -0.01em;
}
.page-table .standalone-table-page .book-ref {
  font-family: var(--serif);
  font-size: 10pt;
  color: #888;
  margin-bottom: 2rem;
  font-style: normal;
}

.tbl-editorial {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.tbl-editorial-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  background: var(--green-card-bg);
  border: 2px solid var(--green-card-border);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  box-shadow: none;
}
.tbl-editorial-body {
  flex: 1;
  min-width: 0;
}
.tbl-editorial-card--idea,
.tbl-editorial-card--ejemplo,
.tbl-editorial-card--aplicacion {
  background: var(--green-card-bg);
  border: 2px solid var(--green-card-border);
}
.tbl-editorial-badge {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  line-height: 1;
}
.tbl-editorial-badge--idea { background: #e8f4fc; }
.tbl-editorial-badge--ejemplo { background: #e8f5e9; }
.tbl-editorial-badge--aplicacion { background: #fef3e8; }
.tbl-editorial-body strong {
  font-family: var(--sans);
  font-size: 7.5pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--green-card-border);
  display: block;
  margin-bottom: 0.4rem;
}
.tbl-editorial-body p {
  font-family: var(--serif);
  font-size: 10pt;
  line-height: 1.55;
  color: #2a2a2a;
  margin: 0;
  overflow-wrap: break-word;
}

/* —— Variante ICONOS — infografía con bloques de color —— */
.page-icons .tbl-editorial-card,
.table-page-icons .tbl-editorial-card {
  background: var(--green-card-bg);
  border: 2px solid var(--green-card-border);
  border-radius: 10px;
  box-shadow: none;
  padding: 0.85rem 1.1rem;
  gap: 0.85rem;
  align-items: flex-start;
}
.page-icons .tbl-editorial-card--idea,
.table-page-icons .tbl-editorial-card--idea,
.page-icons .tbl-editorial-card--ejemplo,
.table-page-icons .tbl-editorial-card--ejemplo,
.page-icons .tbl-editorial-card--aplicacion,
.table-page-icons .tbl-editorial-card--aplicacion {
  background: var(--green-card-bg);
  border: 2px solid var(--green-card-border);
  border-radius: 10px;
}
.page-icons .tbl-editorial-badge,
.table-page-icons .tbl-editorial-badge {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 22px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.page-icons .tbl-editorial-badge--idea,
.table-page-icons .tbl-editorial-badge--idea { background: var(--accent); }
.page-icons .tbl-editorial-badge--ejemplo,
.table-page-icons .tbl-editorial-badge--ejemplo { background: #2d6a4f; }
.page-icons .tbl-editorial-badge--aplicacion,
.table-page-icons .tbl-editorial-badge--aplicacion { background: #4a4a4a; }
.page-icons .tbl-editorial-body strong,
.table-page-icons .tbl-editorial-body strong {
  color: var(--green-card-border);
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.12em;
}
.page-icons .tbl-editorial-body p,
.table-page-icons .tbl-editorial-body p {
  font-size: 9.5pt;
  line-height: 1.45;
  color: #2a2a2a;
}
.page-icons .tbl-editorial,
.table-page-icons .tbl-editorial { gap: 0.35rem; }

.table-page-icons {
  page-break-before: always;
  background: #ffffff;
  padding: 2rem 0 1.5rem;
}
.table-page-icons .standalone-table-page {
  padding: 0 0.5rem;
  max-width: 680px;
  margin: 0 auto;
}
.table-page-icons .standalone-table-page h1 {
  font-family: var(--serif);
  font-size: 22pt;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.35rem;
}
.table-page-icons .standalone-table-page .book-ref {
  font-family: var(--serif);
  font-size: 10pt;
  color: #888;
  margin-bottom: 1.75rem;
}

/* —— Variante MINIMALISTA: mismas tarjetas, sin icono —— */
.page-minimal .tbl-editorial-card {
  border: none;
  border-bottom: 1px solid #ebebeb;
  border-radius: 0;
  box-shadow: none;
  padding: 1.25rem 0;
  gap: 0;
}
.page-minimal .tbl-editorial-card:first-child { padding-top: 0; }
.page-minimal .tbl-editorial-badge { display: none; }
.page-minimal .tbl-editorial-body strong { color: var(--accent-emphasis); font-size: 7pt; }
.page-minimal .tbl-editorial-body p { font-size: 10.5pt; color: #333; }

/* —— Variante COLORIDA (barras azul / verde / dorado) —— */
.page-colorful .tbl-editorial-card,
.table-page-colorful .tbl-editorial-card {
  border: 2px solid var(--green-card-border);
  border-radius: 10px;
  background: var(--green-card-bg);
  box-shadow: none;
  padding: 1.25rem 1.5rem;
  align-items: center;
  gap: 1.15rem;
}
.page-colorful .tbl-editorial-card--idea,
.table-page-colorful .tbl-editorial-card--idea,
.page-colorful .tbl-editorial-card--ejemplo,
.table-page-colorful .tbl-editorial-card--ejemplo,
.page-colorful .tbl-editorial-card--aplicacion,
.table-page-colorful .tbl-editorial-card--aplicacion {
  --card-accent: var(--green-card-border);
  --card-bg: var(--green-card-bg);
}
.page-colorful .tbl-editorial-badge,
.table-page-colorful .tbl-editorial-badge {
  width: auto;
  height: auto;
  min-width: 3.2rem;
  background: transparent;
  font-family: var(--sans);
  font-size: 8pt;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--card-accent);
  padding: 0;
  border-radius: 0;
  align-self: flex-start;
  padding-top: 0.15rem;
}
.page-colorful .tbl-editorial-body strong,
.table-page-colorful .tbl-editorial-body strong {
  color: var(--green-card-border);
  font-size: 7.5pt;
  letter-spacing: 0.1em;
}
.page-colorful .tbl-editorial-body p,
.table-page-colorful .tbl-editorial-body p {
  font-size: 10.5pt;
  line-height: 1.55;
}

.table-page-colorful {
  page-break-before: always;
  background: #ffffff;
  padding: 2rem 0 1.5rem;
}
.table-page-colorful .standalone-table-page {
  padding: 0 0.5rem;
  max-width: 680px;
  margin: 0 auto;
}
.table-page-colorful .standalone-table-page h1 {
  font-family: var(--serif);
  font-size: 22pt;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 0.35rem;
}
.table-page-colorful .standalone-table-page .book-ref {
  font-family: var(--serif);
  font-size: 10pt;
  color: #888;
  margin-bottom: 1.75rem;
}
.table-page-colorful .tbl-editorial { gap: 0.5rem; }

/* —— Imágenes embebidas en PDF —— */
.map-image-wrap, .table-image-wrap {
  margin-top: 1rem;
  page-break-inside: avoid;
  text-align: center;
}

.map-image-wrap img, .table-image-wrap img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.map-image-wrap img { max-height: 240mm; }

* {
  hyphens: none !important;
  -webkit-hyphens: none !important;
}

.summary {
  text-align: left;
}

/* —— Plan de acción (formato original, ligeramente más compacto, 1 página) —— */
.action-plan-page {
  page: action-plan;
  page-break-before: always;
  break-before: page;
  page-break-after: avoid;
  font-family: var(--sans);
  color: #1a2e24;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.ap-sheet {
  display: flex;
  flex-direction: column;
  min-height: calc(297mm - 20mm);
  page-break-inside: avoid;
  break-inside: avoid-page;
}

.ap-header {
  background: #2a5c45;
  color: #fff;
  padding: 2.5mm 5mm 2mm;
  text-align: center;
  flex-shrink: 0;
}

.ap-header h2 {
  font-family: var(--sans);
  font-size: 10.5pt;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin: 0 0 1mm;
  text-transform: uppercase;
  text-align: center;
}

.ap-header .ap-libro-line {
  font-size: 6.5pt;
  opacity: 0.92;
  margin-bottom: 1mm;
}

.ap-header .ap-instruccion {
  font-size: 6.5pt;
  font-style: italic;
  opacity: 0.95;
  margin: 0;
}

.ap-header .ap-cita {
  font-size: 7.5pt;
  color: #b8dcc8;
  line-height: 1.3;
  margin: 0;
}

.ap-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 6.5pt;
  line-height: 1.25;
  flex-shrink: 0;
}

.ap-table col.ap-col-num { width: 6%; }
.ap-table col.ap-col-tema { width: 15%; }
.ap-table col.ap-col-accion { width: 35%; }
.ap-table col.ap-col-check { width: 5%; }
.ap-table col.ap-col-notas { width: 39%; }

.ap-table thead th {
  background: #2a5c45;
  color: #fff;
  font-weight: 700;
  text-align: center;
  padding: 1.5mm 1.5mm;
  border: 1px solid #1e4535;
  vertical-align: middle;
  font-size: 6.2pt;
  letter-spacing: 0.02em;
}

.ap-table tbody td {
  border: 1px solid #c5d9cc;
  padding: 1.2mm 1.5mm;
  vertical-align: top;
}

.ap-table tbody td.ap-col-accion {
  text-align: left;
  padding: 1mm 0.5mm;
}

.ap-table tbody td.ap-col-notas {
  text-align: center;
  padding: 1.2mm 2.5mm;
}

.ap-table tbody tr:nth-child(even) td {
  background: #eef6f0;
}

.ap-col-num { width: 6%; text-align: center; font-weight: 700; }
.ap-col-tema { width: 15%; font-weight: 600; font-size: 6.2pt; text-align: center; vertical-align: top; }
.ap-tema-name { font-weight: 700; margin-bottom: 0.8mm; font-size: 6.2pt; }
.ap-tema-concepto {
  font-weight: 400;
  font-size: 5.8pt;
  line-height: 1.2;
  color: #3d5a4a;
  font-style: italic;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ap-col-accion { width: 35%; text-align: center; }
.ap-col-accion-steps {
  text-align: left;
  font-size: 6.2pt;
  line-height: 1.35;
  padding: 0.15mm 0.3mm;
}
.ap-col-accion-steps .ap-step {
  display: block;
  margin-bottom: 0.35mm;
  padding-left: 0.3mm;
}
.ap-col-accion-steps .ap-step:last-child {
  margin-bottom: 0;
  font-weight: 600;
  color: #1e5631;
}

.ap-col-accion-blank {
  min-height: 9mm;
  width: 100%;
}

.action-plan-page--blank .ap-col-accion-blank {
  min-height: 10mm;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent calc(4mm - 1px),
    #d8e8de calc(4mm - 1px),
    #d8e8de 4mm
  );
}

.ap-col-check { width: 5%; text-align: center; vertical-align: middle; }
.ap-check-box {
  display: inline-block;
  width: 4.5mm;
  height: 4.5mm;
  border: 1.5px solid #2a5c45;
  background: #fff;
  vertical-align: middle;
  box-sizing: border-box;
}
.ap-col-notas { width: 39%; min-height: 7mm; text-align: center; }

.ap-table tbody td.ap-col-tema,
.ap-table tbody td.ap-col-num,
.ap-table tbody td.ap-col-check {
  text-align: center;
}

.ap-section-title {
  background: #2a5c45;
  color: #fff;
  font-size: 6.5pt;
  font-weight: 700;
  letter-spacing: 0.03em;
  padding: 1.5mm 2.5mm;
  margin: 2mm 0 0;
  text-transform: uppercase;
  text-align: center;
  flex-shrink: 0;
}

.ap-weeks {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0;
  border: 1px solid #c5d9cc;
  border-top: none;
  flex-shrink: 0;
}

.ap-week-cell {
  border-right: 1px solid #c5d9cc;
  text-align: center;
  min-height: 7mm;
}

.ap-week-cell:last-child { border-right: none; }

.ap-week-label {
  background: #2a5c45;
  color: #fff;
  font-size: 6.2pt;
  font-weight: 700;
  padding: 1mm 0;
}

.ap-week-box {
  background: #fff;
  min-height: 4mm;
}

.ap-vital-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border: 1px solid #c5d9cc;
  border-top: none;
  flex-shrink: 0;
}

.ap-vital-col {
  border-right: 1px solid #c5d9cc;
  display: flex;
  flex-direction: column;
  min-height: 16mm;
}

.ap-vital-col:last-child { border-right: none; }

.ap-vital-label {
  background: #d4e8dc;
  color: #1a3d2e;
  font-size: 5.8pt;
  font-weight: 700;
  text-align: center;
  padding: 1.2mm 1mm;
  line-height: 1.2;
  min-height: 8mm;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ap-vital-box {
  background: #fff;
  flex: 1 1 auto;
  min-height: 14mm;
}

.ap-notes-area {
  border: 1px solid #c5d9cc;
  border-top: none;
  flex: 1 1 auto;
  min-height: 18mm;
  background: #fff;
}

.ap-footer {
  margin-top: 2mm;
  text-align: center;
  font-size: 5.8pt;
  color: #6b7f75;
  flex-shrink: 0;
}

.ap-disclaimer {
  margin-top: 1.5mm;
  text-align: center;
  font-size: 5.8pt;
  color: #5a6b63;
  font-style: italic;
  line-height: 1.3;
  flex-shrink: 0;
}

/* —— Empieza aquí + mini guía —— */
.guia-page {
  page-break-before: always;
  page-break-after: always;
  padding: 2.5rem 0 2rem;
  font-family: var(--sans);
  color: #1a2e24;
}

.guia-header {
  background: #2a5c45;
  color: #fff;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.75rem;
  text-align: center;
}

.guia-header h2 {
  font-size: 14pt;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin: 0 0 0.35rem;
}

.guia-header p {
  font-size: 9pt;
  opacity: 0.92;
  margin: 0;
}

.guia-block-title {
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2a5c45;
  margin: 0 0 0.75rem;
}

.guia-list {
  list-style: none;
  margin: 0 0 1.75rem;
  padding: 0;
}

.guia-list li {
  font-family: var(--serif);
  font-size: 10.5pt;
  line-height: 1.5;
  color: #2a3d34;
  padding: 0.55rem 0 0.55rem 1.5rem;
  border-bottom: 1px solid #e8ece9;
  position: relative;
}

.guia-list li::before {
  content: "→";
  position: absolute;
  left: 0;
  color: #2a5c45;
  font-weight: 700;
}

.guia-pasos {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.guia-paso {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  border: 2px solid #2a5c45;
  border-radius: 6px;
  padding: 1rem 1.1rem;
  background: #f7fbf8;
}

.guia-paso-num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #2a5c45;
  color: #fff;
  font-weight: 700;
  font-size: 11pt;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guia-paso-text {
  font-family: var(--serif);
  font-size: 11pt;
  line-height: 1.45;
  color: #1a2e24;
  margin: 0;
  padding-top: 0.15rem;
}

/* —— Checklist Pareto (1 página) —— */
.checklist-page {
  page: action-plan;
  page-break-before: always;
  page-break-after: always;
  font-family: var(--sans);
  color: #1a2e24;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.cl-header {
  background: #2a5c45;
  color: #fff;
  padding: 3mm 5mm 2.5mm;
  text-align: center;
}

.cl-header h2 {
  font-size: 11pt;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin: 0 0 1mm;
}

.cl-header p {
  font-size: 7pt;
  opacity: 0.92;
  margin: 0;
  font-style: italic;
}

.cl-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 7pt;
}

.cl-table td {
  border: 1px solid #c5d9cc;
  padding: 2mm 2.5mm;
  vertical-align: middle;
}

.cl-table tr:nth-child(even) td {
  background: #eef6f0;
}

.cl-col-check {
  width: 8%;
  text-align: center;
}

.cl-col-item {
  width: 92%;
  font-family: var(--serif);
  font-size: 8pt;
  line-height: 1.35;
}

.cl-check-box {
  display: inline-block;
  width: 5mm;
  height: 5mm;
  border: 1.5px solid #2a5c45;
  background: #fff;
  box-sizing: border-box;
}

.cl-footer {
  margin-top: 2mm;
  text-align: center;
  font-size: 6pt;
  color: #6b7f75;
  font-style: italic;
}
"""


def esc(text: str) -> str:
    return html.escape(str(text or ""), quote=True)


def split_titulo_autor(libro_nombre: str) -> tuple[str, str]:
    if " - " in libro_nombre:
        titulo, autor = libro_nombre.rsplit(" - ", 1)
        return titulo.strip(), autor.strip()
    return libro_nombre.strip(), ""


def paragraphs(text: str) -> str:
    from src.text_sanitize import clean_resumen_markdown

    text = clean_resumen_markdown(text or "")
    bloques = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not bloques:
        return ""
    return "".join(f"<p>{esc(p)}</p>" for p in bloques)


TABLE_VARIANTS = ("colorida", "minimalista", "iconos")
TABLE_VARIANT_COUNT = len(TABLE_VARIANTS)
TABLE_BADGE_ABBREV = {"idea": "IDEA", "ejemplo": "EJEM", "aplicacion": "APLI"}


def variant_name(variant_index: int) -> str:
    return TABLE_VARIANTS[variant_index % TABLE_VARIANT_COUNT]


def _editorial_card(
    label: str,
    text: str,
    *,
    kind: str,
    badge: str = "",
    extra_class: str = "",
) -> str:
    badge_html = f'<div class="tbl-editorial-badge tbl-editorial-badge--{kind}">{badge}</div>'
    if not badge:
        badge_html = ""
    return f"""
  <div class="tbl-editorial-card tbl-editorial-card--{kind}{extra_class}">
    {badge_html}
    <div class="tbl-editorial-body">
      <strong>{esc(label)}</strong>
      <p>{esc(text)}</p>
    </div>
  </div>"""


def _render_table_editorial(
    tabla: TopicTable,
    *,
    variant: str,
) -> str:
    cards = [
        ("Idea clave", tabla.idea_clave, "idea", "💡"),
        ("Ejemplo práctico", tabla.ejemplo_practico, "ejemplo", "🔧"),
        ("Aplicación en la vida real", tabla.aplicacion_vida_real, "aplicacion", "🎯"),
    ]
    parts = ['<div class="tbl-editorial tbl-editorial-cards">']
    for label, text, kind, icon in cards:
        badge = ""
        if variant == "iconos":
            badge = icon
        elif variant == "colorida":
            badge = TABLE_BADGE_ABBREV.get(kind, kind[:4].upper())
        parts.append(_editorial_card(label, text, kind=kind, badge=badge))
    parts.append("</div>")
    return "".join(parts)


def _render_table_colorful(tabla: TopicTable) -> str:
    return _render_table_editorial(tabla, variant="colorida")


def _render_table_minimal(tabla: TopicTable) -> str:
    return _render_table_editorial(tabla, variant="minimalista")


def _render_table_icons(tabla: TopicTable) -> str:
    return _render_table_editorial(tabla, variant="iconos")


def render_table_fragment(
    tabla: TopicTable,
    *,
    show_label: bool = True,
    variant_index: int = 0,
) -> str:
    variant = variant_index % TABLE_VARIANT_COUNT
    label = (
        '<div class="concept-table-label">Conceptos clave</div>'
        if show_label
        else ""
    )
    renderers = (_render_table_colorful, _render_table_minimal, _render_table_icons)
    body = renderers[variant](tabla)
    return f'<div class="concept-table-wrap">{label}{body}</div>'


def render_table_page_html(
    tabla: TopicTable,
    libro_nombre: str,
    *,
    variant_index: int = 0,
) -> str:
    variant = variant_index % TABLE_VARIANT_COUNT
    page_classes = ("page-colorful page-table", "page-minimal page-table", "page-icons page-table")
    body = f"""
<article class="standalone-table-page">
  <h1>{esc(tabla.tema)}</h1>
  <p class="book-ref">{esc(libro_nombre)}</p>
  {render_table_fragment(tabla, show_label=False, variant_index=variant_index)}
</article>"""
    return wrap_html(
        body,
        title=f"Tabla — {tabla.tema}",
        body_class=page_classes[variant],
    )


def render_map_image_fragment(*, image_rel: str, libro_nombre: str) -> str:
    return f"""
<section class="map-section">
  <div class="section-kicker">Visión general</div>
  <h2 class="section-title">Mapa conceptual</h2>
  <p style="font-size: 9.5pt; color: var(--accent); margin-bottom: 1rem;">{esc(libro_nombre)}</p>
  <div class="map-image-wrap avoid-break">
    <img src="{esc(image_rel)}" alt="Mapa conceptual">
  </div>
</section>"""


CATEGORY_COLORS_TREE = [
    {"bg": "#085041", "light": "#1D9E75", "text": "#9FE1CB", "tema_bg": "#E1F5EE", "tema_text": "#085041"},
    {"bg": "#3C3489", "light": "#7F77DD", "text": "#CECBF6", "tema_bg": "#EEEDFE", "tema_text": "#26215C"},
    {"bg": "#712B13", "light": "#D85A30", "text": "#F5C4B3", "tema_bg": "#FAECE7", "tema_text": "#4A1B0C"},
    {"bg": "#72243E", "light": "#D4537E", "text": "#F4C0D1", "tema_bg": "#FBEAF0", "tema_text": "#4B1528"},
    {"bg": "#0C447C", "light": "#378ADD", "text": "#B5D4F4", "tema_bg": "#E6F1FB", "tema_text": "#042C53"},
    {"bg": "#3B6D11", "light": "#639922", "text": "#C0DD97", "tema_bg": "#EAF3DE", "tema_text": "#173404"},
]


def _map_svg_connectors(num_cols: int) -> str:
    """Conectores desde el nodo raíz hacia cada columna de categoría."""
    if num_cols <= 0:
        return ""
    stroke = "#ccc"
    if num_cols == 1:
        return f"""<svg width="100%" height="52" style="display:block;overflow:visible;margin:0;">
      <line x1="50%" y1="0" x2="50%" y2="52" stroke="{stroke}" stroke-width="2"/>
    </svg>"""
    positions = [(i + 0.5) / num_cols * 100 for i in range(num_cols)]
    lines = [
        f'<line x1="50%" y1="0" x2="50%" y2="18" stroke="{stroke}" stroke-width="2"/>',
        f'<line x1="{positions[0]:.4g}%" y1="18" x2="{positions[-1]:.4g}%" y2="18" stroke="{stroke}" stroke-width="2"/>',
    ]
    for pos in positions:
        lines.append(
            f'<line x1="{pos:.4g}%" y1="18" x2="{pos:.4g}%" y2="52" stroke="{stroke}" stroke-width="2"/>'
        )
    return (
        '<svg width="100%" height="52" style="display:block;overflow:visible;margin:0;">'
        + "".join(lines)
        + "</svg>"
    )


def render_map_fragment(
    temas: list,
    categorias: dict,
    conexiones: list,
    libro_nombre: str,
) -> str:
    por_cat: dict = {}
    cat_colors: dict = {}
    color_idx = 0
    for tema in temas:
        cat = categorias.get(tema, "General")
        por_cat.setdefault(cat, []).append(tema)
        if cat not in cat_colors:
            cat_colors[cat] = CATEGORY_COLORS_TREE[color_idx % len(CATEGORY_COLORS_TREE)]
            color_idx += 1

    titulo, _ = split_titulo_autor(libro_nombre)

    link_words: dict = {}
    for _desde, hasta, rel in conexiones:
        if hasta not in link_words and rel:
            palabras = rel.strip().split()
            link_words[hasta] = " ".join(palabras[:3])

    def cat_block(cat: str, miembros: list, color: dict) -> str:
        bg = color["bg"]
        light = color["light"]
        text = color["text"]
        tema_bg = color["tema_bg"]
        tema_t = color["tema_text"]

        temas_html = ""
        for t in miembros:
            lw = link_words.get(t, "")
            lw_html = (
                f'<div style="font-size:8.5pt;color:#999;font-style:italic;'
                f'margin-bottom:4px;text-align:center;line-height:1.3;">{esc(lw)}</div>'
                if lw
                else ""
            )
            temas_html += f"""
<div style="display:flex;flex-direction:column;align-items:center;">
  {lw_html}
  <div style="background:{tema_bg};color:{tema_t};border:2px solid {light};padding:8px 14px;border-radius:20px;
              font-size:9pt;font-weight:600;text-align:center;min-width:88px;max-width:140px;
              box-shadow:0 1px 4px rgba(0,0,0,0.08);">{esc(t)}</div>
</div>"""

        return f"""
<div style="display:flex;flex-direction:column;align-items:center;flex:1;min-width:0;">
  <div style="background:{bg};color:{text};padding:10px 16px;border-radius:24px;
              font-size:9.5pt;font-weight:600;text-align:center;width:100%;box-sizing:border-box;
              box-shadow:0 2px 8px rgba(0,0,0,0.12);">{esc(cat)}</div>
  <div style="width:2px;height:18px;background:{light};margin:0 auto;"></div>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;width:100%;">
    {temas_html}
  </div>
</div>"""

    cats = list(por_cat.items())
    cols_html = "".join(
        cat_block(cat, miembros, cat_colors[cat]) for cat, miembros in cats
    )
    svg = _map_svg_connectors(len(cats))

    return f"""
<section class="map-section avoid-break">
  <div class="section-kicker">Visión general</div>
  <h2 class="section-title">Mapa conceptual</h2>
  <p style="font-size: 9.5pt; color: var(--accent); margin-bottom: 1.75rem;">{esc(libro_nombre)}</p>

  <div style="display:flex;flex-direction:column;align-items:center;gap:0;width:100%;">

    <div style="background:#1a1a1a;color:#fff;padding:14px 36px;border-radius:14px;
                font-family:var(--sans);font-size:13pt;font-weight:700;text-align:center;
                box-shadow:0 3px 12px rgba(0,0,0,0.18);z-index:2;">
      {esc(titulo)}
    </div>

    {svg}

    <div style="display:flex;flex-direction:row;gap:20px;align-items:flex-start;width:100%;">
      {cols_html}
    </div>

  </div>
</section>"""


def load_map_estructura_data(output_dir: Path) -> Optional[tuple]:
    """Carga temas, categorías y conexiones desde mapa/estructura.json."""
    import json

    from src.output_paths import mapa_estructura_path

    path = mapa_estructura_path(output_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        conexiones = [
            (c["desde"], c["hasta"], c["relacion"])
            for c in data.get("conexiones", [])
        ]
        return (
            data.get("temas", []),
            data.get("categorias", {}),
            conexiones,
            data.get("libro_nombre", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def render_map_page_html(
    temas: list,
    categorias: dict,
    conexiones: list,
    libro_nombre: str,
) -> str:
    body = render_map_fragment(temas, categorias, conexiones, libro_nombre)
    return wrap_html(body, title=f"Mapa — {libro_nombre}")


def render_cover_fragment(
    libro_nombre: str,
    *,
    introduccion: str,
    fecha: datetime,
    num_temas: int,
    voz_nombre: str,
    titulo_comercial: str = "",
    subtitulo_portada: str = "",
    imagen_portada: str = "",
    serie_label: str = "",
) -> str:
    titulo, autor = split_titulo_autor(libro_nombre)
    comercial = (titulo_comercial or "").strip()
    subtitulo = (subtitulo_portada or titulo).strip()
    if not serie_label.strip():
        serie_label = "Resumen personal"
    meta = (
        f"Por {esc(voz_nombre)} · {fecha.strftime('%d/%m/%Y')} · {num_temas} temas"
    )
    hero_html = ""
    if "pareto" in titulo.lower() or "pareto" in comercial.lower():
        hero_html = """
    <div class="cover-hero">
      <span class="cover-hero-80">80</span>
      <span class="cover-hero-20">/20</span>
    </div>"""

    if comercial:
        titulo_block = f'<h1 class="cover-title">{esc(comercial)}</h1>'
        sub_parts = [esc(subtitulo)]
        if autor:
            sub_parts.append(esc(autor))
        titulo_block += f'<div class="cover-subtitle">{" · ".join(sub_parts)}</div>'
        autor_block = ""
    else:
        titulo_block = f'<h1 class="cover-title">{esc(titulo)}</h1>'
        autor_block = f'<div class="cover-author">{esc(autor)}</div>' if autor else ""

    photo_html = ""
    if imagen_portada:
        photo_html = f"""
    <div class="cover-photo-wrap">
      <img src="{esc(imagen_portada)}" alt="Psicopedagoga en intervención educativa">
    </div>"""

    return f"""
<section class="cover">
  <div class="cover-top">
    <div class="cover-label">{esc(serie_label)}</div>{hero_html}
    {autor_block}
  </div>{photo_html}
  {titulo_block}
</section>
<div class="cover-dot"></div>
<div class="cover-meta">{meta}</div>"""


def _format_oficio(audiencia: str) -> str:
    """Ej. «psicopedagoga en escuela» → «Psicopedagoga»."""
    texto = (audiencia or "").strip()
    if " en " in texto:
        texto = texto.split(" en ", 1)[0].strip()
    if not texto:
        return ""
    return texto[0].upper() + texto[1:]


def render_audiencia_page(
    contexto: dict,
    *,
    intro_audiencia: str = "",
    aviso_legal: str = "",
) -> str:
    from src.action_plan import AVISO_MATERIAL_APOYO

    audiencia = str(contexto.get("audiencia", "") or "").strip()
    oficio = _format_oficio(audiencia)
    intro_audiencia = (intro_audiencia or "").strip()
    reto = contexto.get("reto", "")
    intento = contexto.get("intento_fallido", "")
    aviso = (aviso_legal or AVISO_MATERIAL_APOYO).strip()

    if not oficio and not intro_audiencia:
        return ""

    extras = ""
    if reto:
        extras += (
            f'<div class="perfil-item">'
            f'<div class="perfil-label">Su mayor reto</div>'
            f'<div class="perfil-valor">{esc(reto)}</div>'
            f"</div>"
        )
    if intento:
        extras += (
            f'<div class="perfil-item">'
            f'<div class="perfil-label">Lo que intentó</div>'
            f'<div class="perfil-valor">{esc(intento)}</div>'
            f"</div>"
        )

    intro_html = (
        f'<p class="perfil-audiencia">{esc(intro_audiencia)}</p>'
        if intro_audiencia
        else ""
    )
    disclaimer_html = (
        f'<div class="audiencia-aviso" role="note">'
        f'<div class="audiencia-aviso-label">Aviso</div>'
        f'<p class="audiencia-aviso-text">{esc(aviso)}</p>'
        f"</div>"
    )

    return f"""
<section class="audiencia-page">
  <div class="perfil-header">
    <div class="perfil-rule"></div>
    <div class="perfil-titulo">Para quién es este resumen</div>
  </div>
  <div class="perfil-items">
    <div class="perfil-item">
      <div class="perfil-label">Oficio</div>
      <div class="perfil-valor">{esc(oficio)}</div>
    </div>
    {extras}
  </div>
  {intro_html}
  {disclaimer_html}
</section>"""


def render_guia_inicio_fragment(extras) -> str:
    """Página «Empieza aquí»: mini guía (5 líneas) + 3 pasos iniciales."""
    from src.product_extras import ProductExtras

    if not isinstance(extras, ProductExtras):
        return ""
    if not extras.mini_guia and not extras.empieza_pasos:
        return ""

    guia_items = "".join(f"<li>{esc(linea)}</li>" for linea in extras.mini_guia[:5])
    pasos_html = []
    for i, paso in enumerate(extras.empieza_pasos[:3], 1):
        pasos_html.append(
            f'<li class="guia-paso">'
            f'<span class="guia-paso-num">{i}</span>'
            f'<p class="guia-paso-text">{esc(paso)}</p>'
            f"</li>"
        )

    return f"""
<section class="guia-page">
  <div class="guia-block-title">Mini guía · Cómo usar este material en menos de 10 minutos</div>
  <ul class="guia-list">{guia_items}</ul>
  <div class="guia-block-title">Tus 3 primeros pasos</div>
  <ol class="guia-pasos">{"".join(pasos_html)}</ol>
</section>"""


def render_checklist_fragment(extras) -> str:
    """Checklist imprimible «¿Estoy aplicando Pareto?» (1 página)."""
    from src.product_extras import ProductExtras

    if not isinstance(extras, ProductExtras) or not extras.checklist_items:
        return ""

    rows = []
    for item in extras.checklist_items:
        rows.append(
            f"""<tr>
  <td class="cl-col-check"><span class="cl-check-box"></span></td>
  <td class="cl-col-item">{esc(item)}</td>
</tr>"""
        )

    return f"""
<section class="checklist-page">
  <header class="cl-header">
    <h2>{esc(extras.checklist_titulo)}</h2>
    <p>Marca sí/no al cerrar cada semana</p>
  </header>
  <table class="cl-table">
    <tbody>
{"".join(rows)}
    </tbody>
  </table>
  <p class="cl-footer">Si marcaste 7 o más, estás aplicando el principio. Si no, ajusta la semana siguiente.</p>
</section>"""


def render_perfil_lector(
    contexto: dict,
    voz_nombre: str,
    *,
    introduccion: str = "",
    intro_audiencia: str = "",
    autor_ocupacion: str = "",
) -> str:
    from src.config import AUTOR_OCUPACION

    autor_ocupacion = autor_ocupacion or AUTOR_OCUPACION
    intro = (introduccion or "").strip()

    if not intro and not autor_ocupacion:
        return ""

    intro_html = f'<p class="perfil-intro">{esc(intro)}</p>' if intro else ""
    from src.config import AUTOR_BIO_CORTA

    quien_soy = AUTOR_BIO_CORTA if AUTOR_BIO_CORTA else autor_ocupacion
    items_html = (
        f'<div class="perfil-item">'
        f'<div class="perfil-label">¿Quién soy?</div>'
        f'<div class="perfil-valor">{esc(quien_soy)}</div>'
        f"</div>"
    )

    return f"""
<section class="perfil-lector">
  <div class="perfil-header">
    <div class="perfil-rule"></div>
    <div class="perfil-titulo">Por qué leí este libro</div>
    <div class="perfil-nombre">{esc(voz_nombre)}</div>
  </div>
  {intro_html}
  <div class="perfil-items">{items_html}</div>
</section>"""


def render_topic_fragment(
    resultado: TopicResult,
    *,
    index: int,
    voz_nombre: str,
    tabla: TopicTable | None = None,
) -> str:
    texto = resultado.resumen_voz or resultado.resumen
    tabla_html = ""
    if tabla is not None:
        tabla_html = f"""
<section class="topic-tables">
  <div class="page-icons">{_render_table_icons(tabla)}</div>
</section>"""
    from src.config import TEMA_RESUMEN_ETIQUETA

    return f"""
<section class="topic">
  <header class="topic-header">
    <div class="topic-number">Tema {index:02d}</div>
    <h2 class="topic-title">{esc(resultado.tema)}</h2>
    <div class="topic-voice">{esc(TEMA_RESUMEN_ETIQUETA)}</div>
  </header>
  <div class="summary">{paragraphs(texto)}</div>
</section>{tabla_html}"""


def render_table_pdf_page(tabla: TopicTable, libro_nombre: str) -> str:
    """Página de tabla con iconos embebida en el PDF (HTML directo, sin PNG)."""
    return f"""
<section class="table-page-icons page-icons">
  <article class="standalone-table-page">
    <h1>{esc(tabla.tema)}</h1>
    <p class="book-ref">{esc(libro_nombre)}</p>
    {_render_table_icons(tabla)}
  </article>
</section>"""


def _audiencia_desde_output(output_dir: Path) -> str:
    from src.topic_intros_store import load_topic_intros

    _, audiencia = load_topic_intros(output_dir)
    if audiencia:
        return audiencia
    contexto_path = Path(output_dir) / "contexto_usuario.json"
    try:
        ctx = json.loads(contexto_path.read_text(encoding="utf-8"))
        return str(ctx.get("audiencia", "") or ctx.get("ocupacion", "") or "")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ""


def _format_accion_celda(texto: str) -> str:
    """Pasos con viñetas (formato original)."""
    partes = [p.strip() for p in (texto or "").split("·") if p.strip()]
    if len(partes) >= 2:
        items = []
        for parte in partes:
            items.append(f'<span class="ap-step">• {esc(parte)}</span>')
        return f'<div class="ap-col-accion-steps">{"".join(items)}</div>'
    return esc(texto)


_AP_TABLE_COLGROUP = """
    <colgroup>
      <col class="ap-col-num" style="width:6%">
      <col class="ap-col-tema" style="width:15%">
      <col class="ap-col-accion" style="width:35%">
      <col class="ap-col-check" style="width:5%">
      <col class="ap-col-notas" style="width:39%">
    </colgroup>"""


def _action_plan_row_html(row, *, blank_actions: bool) -> str:
    tema_html = f'<div class="ap-tema-name">{esc(row.tema)}</div>'
    if not blank_actions and getattr(row, "concepto_libro", ""):
        tema_html += f'<div class="ap-tema-concepto">{esc(row.concepto_libro)}</div>'
    if blank_actions:
        accion_html = '<div class="ap-col-accion-blank"></div>'
    else:
        accion_html = _format_accion_celda(row.accion_concreta)
    return f"""<tr>
  <td class="ap-col-num">{esc(row.numero)}</td>
  <td class="ap-col-tema">{tema_html}</td>
  <td class="ap-col-accion">{accion_html}</td>
  <td class="ap-col-check"><span class="ap-check-box"></span></td>
  <td class="ap-col-notas"></td>
</tr>"""


def _render_action_plan_sheet(
    plan,
    *,
    blank_actions: bool = False,
    titulo: str | None = None,
    instruccion: str | None = None,
    show_disclaimer: bool = True,
    extra_class: str = "",
) -> str:
    n = len(plan.filas)
    rows_html = [
        _action_plan_row_html(row, blank_actions=blank_actions) for row in plan.filas
    ]
    weeks = "".join(
        f'<div class="ap-week-cell"><div class="ap-week-label">S{i}</div><div class="ap-week-box"></div></div>'
        for i in range(1, n + 1)
    )
    v = plan.vital_20
    header_titulo = titulo if titulo is not None else plan.titulo_plan
    header_instruccion = instruccion if instruccion is not None else plan.instruccion
    page_class = "action-plan-page"
    if extra_class:
        page_class += f" {extra_class}"
    disclaimer_html = (
        f'  <p class="ap-disclaimer">{esc(plan.aviso_legal)}</p>'
        if show_disclaimer
        else ""
    )

    return f"""
<section class="{page_class}">
  <div class="ap-sheet">
  <header class="ap-header">
    <h2>{esc(header_titulo)}</h2>
    <div class="ap-libro-line">{esc(plan.libro_line)}</div>
    {f'<p class="ap-instruccion">{esc(header_instruccion)}</p>' if header_instruccion.strip() else ''}
    {f'<p class="ap-cita">{esc(plan.cita)}</p>' if plan.cita.strip() and not blank_actions else ''}
  </header>
  <table class="ap-table">
{_AP_TABLE_COLGROUP}
    <thead>
      <tr>
        <th class="ap-col-num">#</th>
        <th class="ap-col-tema">TEMA</th>
        <th class="ap-col-accion">ACCIÓN CONCRETA</th>
        <th class="ap-col-check">✓</th>
        <th class="ap-col-notas">SEMANA NOTAS</th>
      </tr>
    </thead>
    <tbody>
{"".join(rows_html)}
    </tbody>
  </table>
  <div class="ap-section-title">RASTREADOR DE SEMANAS</div>
  <div class="ap-weeks">{weeks}</div>
  <div class="ap-section-title">MI 20% VITAL · Completa esto antes de empezar</div>
  <div class="ap-vital-grid">
    <div class="ap-vital-col"><div class="ap-vital-label">{esc(v.col1)}</div><div class="ap-vital-box"></div></div>
    <div class="ap-vital-col"><div class="ap-vital-label">{esc(v.col2)}</div><div class="ap-vital-box"></div></div>
    <div class="ap-vital-col"><div class="ap-vital-label">{esc(v.col3)}</div><div class="ap-vital-box"></div></div>
    <div class="ap-vital-col"><div class="ap-vital-label">{esc(v.col4)}</div><div class="ap-vital-box"></div></div>
  </div>
  <div class="ap-section-title">MIS NOTAS</div>
  <div class="ap-notes-area"></div>
  <footer class="ap-footer">{esc(plan.footer)}</footer>
{disclaimer_html}
  </div>
</section>"""


def render_action_plan_fragment(plan) -> str:
    """Plan de acción: hoja con acciones + hoja en blanco opcional para rellenar."""
    from src.action_plan import ActionPlan

    if not isinstance(plan, ActionPlan) or not plan.filas:
        return ""

    filled = _render_action_plan_sheet(plan, blank_actions=False)
    if not plan.incluir_plantilla_vacia:
        return filled

    blank = _render_action_plan_sheet(
        plan,
        blank_actions=True,
        titulo=plan.titulo_plantilla_vacia,
        instruccion=plan.instruccion_plantilla_vacia,
        show_disclaimer=False,
        extra_class="action-plan-page--blank",
    )
    return filled + blank


def render_book_html(
    package: BookPackage,
    *,
    voz_nombre: str = "Yordy",
    html_dir: Optional[Path] = None,
) -> str:
    from src.output_paths import html_dir as book_html_dir

    fecha = package.fecha or datetime.now()
    intro = package.introduccion or (
        f"Recopilo aquí lo que aprendí al leer «{package.libro_nombre}»."
    )
    tablas_map = {t.tema: t for t in package.tablas}
    html_dir = Path(html_dir or book_html_dir(package.output_dir))

    contexto: dict = {}
    contexto_path = Path(package.output_dir) / "contexto_usuario.json"
    try:
        contexto = json.loads(contexto_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    intro_audiencia = ""
    try:
        from src.output_paths import intro_audiencia_path

        ap = intro_audiencia_path(package.output_dir)
        if ap.exists():
            intro_audiencia = ap.read_text(encoding="utf-8").strip()
    except (OSError, ImportError):
        pass

    perfil_html = render_perfil_lector(contexto, voz_nombre, introduccion=intro)

    from src.action_plan import AVISO_MATERIAL_APOYO, load_action_plan

    action_plan = load_action_plan(package.output_dir)
    aviso_legal = action_plan.aviso_legal if action_plan else AVISO_MATERIAL_APOYO

    audiencia_html = render_audiencia_page(
        contexto,
        intro_audiencia=intro_audiencia,
        aviso_legal=aviso_legal,
    )

    from src.product_extras import ensure_product_extras

    audiencia_str = str(contexto.get("audiencia", "") or contexto.get("ocupacion", "") or "")
    reto_str = str(contexto.get("reto", "") or "")
    familia_rol = ""
    try:
        from src.rol_usuario import load_rol_perfil

        perfil = load_rol_perfil(package.output_dir)
        if perfil:
            familia_rol = str(perfil.familia_rol or "")
            if not reto_str:
                reto_str = str(perfil.reto or "")
    except ImportError:
        pass

    num_semanas = len(action_plan.filas) if action_plan and action_plan.filas else 10
    num_temas = len([r for r in package.resultados if not r.fallo])
    producto = ensure_product_extras(
        package.output_dir,
        libro_nombre=package.libro_nombre,
        audiencia=audiencia_str,
        num_semanas=num_semanas,
        familia_rol=familia_rol,
        reto=reto_str,
    )

    from src.serie import ensure_kdp_listing

    ensure_kdp_listing(
        package.output_dir,
        libro_nombre=package.libro_nombre,
        audiencia=audiencia_str,
        familia_rol=familia_rol,
        reto=reto_str,
        num_temas=num_temas,
        num_semanas=num_semanas,
    )
    guia_html = render_guia_inicio_fragment(producto)
    checklist_html = render_checklist_fragment(producto)

    imagen_portada_rel = ""
    if producto.imagen_portada:
        img_path = Path(package.output_dir) / producto.imagen_portada
        if img_path.is_file():
            imagen_portada_rel = rel_path(book_html_dir(package.output_dir), img_path)

    parts = [
        render_cover_fragment(
            package.libro_nombre,
            introduccion=intro,
            fecha=fecha,
            num_temas=num_temas,
            voz_nombre=voz_nombre,
            titulo_comercial=producto.titulo_comercial,
            subtitulo_portada=producto.subtitulo_portada,
            imagen_portada=imagen_portada_rel,
            serie_label=producto.serie_nombre or "",
        )
    ]
    if perfil_html:
        parts.append(perfil_html)
    if guia_html:
        parts.append(guia_html)
    if audiencia_html:
        parts.append(audiencia_html)

    mapa_data = load_map_estructura_data(package.output_dir)
    if mapa_data:
        temas, categorias, conexiones, libro_mapa = mapa_data
        parts.append(
            render_map_fragment(
                temas,
                categorias,
                conexiones,
                libro_mapa or package.libro_nombre,
            )
        )
    elif package.mapa_path and Path(package.mapa_path).exists():
        map_rel = rel_path(html_dir, Path(package.mapa_path))
        parts.append(
            render_map_image_fragment(
                image_rel=map_rel,
                libro_nombre=package.libro_nombre,
            )
        )

    idx = 0
    for resultado in package.resultados:
        if resultado.fallo:
            continue
        idx += 1
        tabla = tablas_map.get(resultado.tema)
        parts.append(
            render_topic_fragment(
                resultado,
                index=idx,
                voz_nombre=voz_nombre,
                tabla=tabla,
            )
        )

    action_html = render_action_plan_fragment(action_plan)
    if checklist_html:
        parts.append(checklist_html)
    if action_html:
        parts.append(action_html)

    return wrap_html("".join(parts), title=package.libro_nombre)


def rel_path(from_dir: Path, target: Path) -> str:
    from_dir = Path(from_dir).resolve()
    target = Path(target).resolve()
    try:
        return Path(target).relative_to(from_dir).as_posix()
    except ValueError:
        import os
        return Path(os.path.relpath(target, from_dir)).as_posix()


def wrap_html(body: str, *, title: str = "Resumen", body_class: str = "") -> str:
    class_attr = f' class="{body_class}"' if body_class else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>{EDITORIAL_CSS}</style>
</head>
<body{class_attr}>
{body}
</body>
</html>"""


def write_html(path: Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def html_to_png(html_path: Path, png_path: Path) -> Path:
    """Renderiza una página HTML a PNG con Playwright."""
    from playwright.sync_api import sync_playwright

    html_path = Path(html_path).resolve()
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()

    return png_path


def html_to_pdf(html_path: Path, pdf_path: Path, *, title: str = "") -> Path:
    """Convierte un archivo HTML local a PDF con Playwright/Chromium."""
    from playwright.sync_api import sync_playwright

    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    file_url = html_path.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url, wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            display_header_footer=False,
        )
        browser.close()

    return pdf_path


def html_string_to_pdf(html_content: str, html_path: Path, pdf_path: Path) -> Path:
    write_html(html_path, html_content)
    return html_to_pdf(html_path, pdf_path)

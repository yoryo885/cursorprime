"""Genera embudo completo HTML para un cliente."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from funnel_html import (
    generar_index_embudo,
    generar_landing_html,
    generar_propuesta_html,
    generar_whatsapp_html,
)

ROOT = Path(__file__).resolve().parent.parent
CURSORPRIME = ROOT.parent.parent
MARKETING = CURSORPRIME / "marketing-audit"
CLIENTES = CURSORPRIME / "clientes"


def _load_json(path: Path, default: dict | None = None) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default or {}


def run_embudo(cliente: str = "clinica-sol", proyecto: str = "audit-inicial", slug: str = "demo-clinica-sol") -> int:
    brief = ROOT / "data" / "clinica-sol" / "inputs" / "brief.json"
    cmd = [
        sys.executable,
        str(MARKETING / "marketing_audit_main.py"),
        "audit",
        "--brief",
        str(brief),
        "--slug",
        slug,
        "--cliente",
        cliente,
        "--proyecto",
        proyecto,
        "--reset-checkpoint",
    ]
    print("→ Paso 1: generando informe de marketing…\n")
    r = subprocess.run(cmd, cwd=MARKETING)
    if r.returncode != 0:
        return r.returncode

    audit_out = MARKETING / "data" / slug / "output"
    entregables = CLIENTES / cliente / "proyectos" / proyecto / "entregables"
    paso1 = entregables / "paso-1-informe"
    paso2 = entregables / "paso-2-propuesta"
    paso3 = entregables / "paso-3-web"
    paso4 = entregables / "paso-4-whatsapp"

    for d in (paso1, paso2, paso3, paso4):
        d.mkdir(parents=True, exist_ok=True)

    # Paso 1 — informe
    audit_html = audit_out / "MARKETING-AUDIT.html"
    if audit_html.exists():
        shutil.copy2(audit_html, paso1 / "index.html")
        nav = """
  <p style="margin-top:1.5rem;font-size:0.85rem;text-align:center;border-top:1px solid #e7e5e4;padding-top:1rem">
    <a href="../index.html">← Embudo completo</a> ·
    <a href="../paso-2-propuesta/index.html">Paso 2: Propuesta</a>
  </p>"""
        html = (paso1 / "index.html").read_text(encoding="utf-8")
        if "../index.html" not in html:
            html = html.replace("</body>", nav + "\n</body>")
            (paso1 / "index.html").write_text(html, encoding="utf-8")
    logo_src = audit_out / "logo.svg"
    if not logo_src.exists():
        logo_src = MARKETING / "assets" / "logo.svg"
    if logo_src.exists():
        shutil.copy2(logo_src, paso1 / "logo.svg")
    for name in ("MARKETING-AUDIT.md", "audit.json"):
        src = audit_out / name
        if src.exists():
            shutil.copy2(src, paso1 / name)

    branding = _load_json(MARKETING / "meta" / "report_branding.json")
    perfil = _load_json(CLIENTES / cliente / "perfil.json")
    audit = _load_json(audit_out / "audit.json", {})
    score = audit.get("overall_score", 55)

    perfil_cliente = {
        "nombre": perfil.get("nombre") or audit.get("brand_name", cliente),
        "ciudad": perfil.get("ciudad", "Santiago, Chile"),
        "whatsapp": branding.get("whatsapp", ""),
    }

    print("→ Paso 2: propuesta comercial HTML…")
    generar_propuesta_html(paso2 / "index.html", branding, perfil_cliente, score)

    print("→ Paso 3: web propuesta HTML…")
    generar_landing_html(paso3 / "index.html", perfil_cliente, branding)

    print("→ Paso 4: simulación WhatsApp HTML…")
    generar_whatsapp_html(paso4 / "index.html", perfil_cliente, branding)

    pasos = [
        {"num": 1, "titulo": "Informe de marketing", "desc": "Audit 55/100 · lenguaje claro · listo para enviar", "href": "paso-1-informe/index.html", "listo": True},
        {"num": 2, "titulo": "Propuesta comercial", "desc": "3 planes: $80k · $120k · $180k / mes", "href": "paso-2-propuesta/index.html", "listo": True},
        {"num": 3, "titulo": "Web propuesta", "desc": "Landing con CTA, FAQ y «Por qué elegirnos»", "href": "paso-3-web/index.html", "listo": True},
        {"num": 4, "titulo": "Bot WhatsApp", "desc": "Simulación agendar hora · demo sin API", "href": "paso-4-whatsapp/index.html", "listo": True},
    ]
    print("→ Índice del embudo…")
    generar_index_embudo(entregables / "index.html", perfil_cliente["nombre"], branding, pasos)

    # Copiar propuesta MD si existe
    prop_md = CLIENTES / cliente / "proyectos" / proyecto / "entregables" / "estrategia" / "CLIENT-PROPOSAL.md"
    if prop_md.exists():
        shutil.copy2(prop_md, paso2 / "CLIENT-PROPOSAL.md")

    print(f"\n✅ Embudo completo: {entregables}/index.html")
    print(f"   paso-1-informe/index.html")
    print(f"   paso-2-propuesta/index.html")
    print(f"   paso-3-web/index.html")
    print(f"   paso-4-whatsapp/index.html")
    return 0

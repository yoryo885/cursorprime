"""Estado de módulos cursorprime — hecho / parcial / falta."""

from __future__ import annotations

from pathlib import Path

from src.config import CURSORPRIME, PROYECTOS, load_json


def _exists(*parts) -> bool:
    return Path(CURSORPRIME, *parts).exists()


def _cli(name: str) -> bool:
    p = CURSORPRIME / name
    if not p.is_dir():
        return False
    return bool(list(p.glob("*_main.py")) or (p / "main.py").exists())


def _launchd_radar_instalado() -> bool:
    return (Path.home() / "Library/LaunchAgents/com.cursorprime.radar-kdp.plist").exists()


def _analisis_radar_live_ok() -> bool:
    state = load_json(CURSORPRIME / "analisis-de-proyectos/meta/radar_auto_state.json", {}) or {}
    corrida = state.get("ultima_corrida") or {}
    if not corrida.get("ok"):
        return False
    slug = corrida.get("slug")
    if not slug:
        return False
    fetch = load_json(CURSORPRIME / "analisis-de-proyectos/data" / slug / "meta/fetch.json", {}) or {}
    return fetch.get("mode") == "live" or fetch.get("mock") is False


def _analisis_export_evaluado() -> bool:
    ideas = CURSORPRIME / "ideas de proyectos/ideas/from-analisis"
    evals = CURSORPRIME / "ideas de proyectos/evaluaciones"
    if not ideas.exists():
        return False
    for p in ideas.glob("*.json"):
        d = load_json(p, {}) or {}
        slug = d.get("slug")
        if slug and (evals / slug / "veredicto.json").exists():
            return True
    return False


def _analisis_encadenar_ok() -> bool:
    return _exists("analisis-de-proyectos", "src", "encadenar.py") and _analisis_export_evaluado()


CAPA_CREADOR = "creador"
CAPA_PRODUCTO = "producto"

MODULO_SECCIONES = {
    CAPA_CREADOR: {
        "titulo": "Creador de proyectos",
        "subtitulo": "Tu fábrica cursorprime — investiga, evalúa y diseña pipelines antes de construir.",
    },
    CAPA_PRODUCTO: {
        "titulo": "Proyectos creados",
        "subtitulo": "Pipelines y productos que salieron del creador — comercial, contenido y operación.",
    },
}

def modulos_estado() -> list[dict]:
    """Módulos con checklist automático según archivos en disco."""
    items = [
        {
            "id": "router",
            "nombre": "Router + skills",
            "carpeta": "router.py",
            "grupo": "core",
            "capa": CAPA_CREADOR,
            "hecho": [_exists("router.py"), _exists("meta", "router.json"), _exists("AGENTS.md")],
            "falta": [],
        },
        {
            "id": "analisis",
            "nombre": "Análisis de proyectos",
            "carpeta": "analisis-de-proyectos",
            "grupo": "investigacion",
            "capa": CAPA_CREADOR,
            "hecho": [
                _cli("analisis-de-proyectos"),
                _exists("analisis-de-proyectos", "src", "agents", "fetch_agent.py"),
                _exists("analisis-de-proyectos", "src", "radar_scheduler.py"),
                _exists("analisis-de-proyectos", "scripts", "radar-semanal.sh"),
                _exists("analisis-de-proyectos", "scripts", "com.cursorprime.radar-kdp.plist"),
                _analisis_radar_live_ok(),
                _launchd_radar_instalado(),
                _analisis_export_evaluado(),
                _analisis_encadenar_ok(),
            ],
            "falta": [
                "Síntesis con LLM (hoy heurística)",
                "Informe HTML del análisis (solo markdown)",
            ],
        },
        {
            "id": "lluvia",
            "nombre": "Lluvia de ideas",
            "carpeta": "lluvia-de-ideas",
            "grupo": "investigacion",
            "capa": CAPA_CREADOR,
            "hecho": [_cli("lluvia-de-ideas")],
            "falta": [],
        },
        {
            "id": "ideas",
            "nombre": "Ideas + evaluar",
            "carpeta": "ideas de proyectos",
            "grupo": "investigacion",
            "capa": CAPA_CREADOR,
            "hecho": [_exists("ideas de proyectos", "evaluar.py")],
            "falta": [],
        },
        {
            "id": "project_lens",
            "nombre": "Project Lens (profundo)",
            "carpeta": "project_lens",
            "grupo": "investigacion",
            "capa": CAPA_CREADOR,
            "hecho": [_cli("project_lens")],
            "falta": ["Web real (--no-mock-web + Playwright)"],
        },
        {
            "id": "prompts",
            "nombre": "Creador de prompts",
            "carpeta": "creador de prompts",
            "grupo": "meta",
            "capa": CAPA_CREADOR,
            "hecho": [_cli("creador de prompts")],
            "falta": [],
        },
        {
            "id": "skills",
            "nombre": "Creador de skills",
            "carpeta": "creador de skills",
            "grupo": "meta",
            "capa": CAPA_CREADOR,
            "hecho": [_cli("creador de skills")],
            "falta": [],
        },
        {
            "id": "panel",
            "nombre": "Centro de control",
            "carpeta": "centro de control prime",
            "grupo": "meta",
            "capa": CAPA_CREADOR,
            "hecho": [_cli("centro de control prime")],
            "falta": [],
        },
        {
            "id": "marketing_audit",
            "nombre": "Marketing Audit",
            "carpeta": "marketing-audit",
            "grupo": "comercial",
            "capa": CAPA_PRODUCTO,
            "hecho": [_cli("marketing-audit"), _exists("marketing-audit", "src", "html_report.py")],
            "falta": ["PDF --pdf", "Audit URL real (MOCK_FETCH=false)", "Outreach automático"],
        },
        {
            "id": "clientes",
            "nombre": "Capa clientes",
            "carpeta": "clientes",
            "grupo": "comercial",
            "capa": CAPA_PRODUCTO,
            "hecho": [_exists("clientes", "_plantilla"), _exists("clientes", "clinica-sol")],
            "falta": ["1 cliente real que pague"],
        },
        {
            "id": "embudo",
            "nombre": "Embudo comercial HTML",
            "carpeta": "proyectos-top3",
            "grupo": "comercial",
            "capa": CAPA_PRODUCTO,
            "hecho": [
                _exists("proyectos-top3", "01-auditorias-locales", "auditorias_main.py"),
                _exists("clientes", "clinica-sol", "proyectos", "audit-inicial", "entregables", "index.html"),
            ],
            "falta": ["Propuesta HTML auto desde pipeline", "Deploy web real"],
        },
        {
            "id": "wasap",
            "nombre": "Bot WhatsApp pymes",
            "carpeta": "proyectos-top3/02-wasap-pymes",
            "grupo": "comercial",
            "capa": CAPA_PRODUCTO,
            "hecho": [_exists("proyectos-top3", "02-wasap-pymes", "wasap_main.py")],
            "falta": ["API Meta", "Webhook live", "1 piloto"],
        },
        {
            "id": "presencia",
            "nombre": "Presencia web locales",
            "carpeta": "proyectos-top3/03-presencia-digital",
            "grupo": "comercial",
            "capa": CAPA_PRODUCTO,
            "hecho": [_exists("proyectos-top3", "03-presencia-digital", "presencia_main.py")],
            "falta": ["HTML deploy", "Google Business Profile"],
        },
        {
            "id": "contenido",
            "nombre": "Creador de contenido",
            "carpeta": "creador de contenido",
            "grupo": "produccion",
            "capa": CAPA_PRODUCTO,
            "hecho": [_cli("creador de contenido")],
            "falta": ["Video Kling API real"],
        },
        {
            "id": "libros",
            "nombre": "Libros / KDP",
            "carpeta": "libros a entender",
            "grupo": "produccion",
            "capa": CAPA_PRODUCTO,
            "hecho": [_exists("libros a entender", "main.py"), _exists("libros a entender", "kdp_main.py")],
            "falta": ["Correr con PDF usuario"],
        },
        {
            "id": "linkedin",
            "nombre": "LinkedIn ghostwriter",
            "carpeta": "linkedin-ghostwriter",
            "grupo": "produccion",
            "capa": CAPA_PRODUCTO,
            "hecho": [_exists("linkedin-ghostwriter", "generar_posts.py")],
            "falta": ["Mes de posts real"],
        },
    ]

    out = []
    for m in items:
        hecho_checks = [h for h in m["hecho"] if h is True]
        hecho_n = len(hecho_checks)
        total_checks = len(m["hecho"])
        falta = list(m.get("falta") or [])
        if total_checks == 0:
            pct = 100 if not falta else 50
        else:
            pct = round((hecho_n / total_checks) * 100)
            if falta:
                pct = min(pct, 85)

        if pct >= 90 and not falta:
            estado = "hecho"
        elif pct >= 40 or hecho_n > 0:
            estado = "parcial"
        else:
            estado = "falta"

        out.append(
            {
                **{k: v for k, v in m.items() if k not in ("hecho", "falta")},
                "estado": estado,
                "avance_pct": pct,
                "hecho_count": hecho_n,
                "checks_total": total_checks,
                "pendientes": falta,
            }
        )
    return out


def embudo_comercial() -> list[dict]:
    base = "clientes/clinica-sol/proyectos/audit-inicial/entregables"
    return [
        {
            "paso": 1,
            "slug": "paso-1-informe",
            "nombre": "Informe de marketing",
            "desc": "Audit 55/100 · lenguaje claro · listo para enviar",
            "path": f"{base}/paso-1-informe/index.html",
            "estado": "demo",
            "listo": True,
            "falta": "URL real + 1 cliente paga",
        },
        {
            "paso": 2,
            "slug": "paso-2-propuesta",
            "nombre": "Propuesta comercial",
            "desc": "3 planes: $80k · $120k · $180k / mes",
            "path": f"{base}/paso-2-propuesta/index.html",
            "estado": "demo",
            "listo": True,
            "falta": "Pipeline auto encadenado",
        },
        {
            "paso": 3,
            "slug": "paso-3-web",
            "nombre": "Web presencia",
            "desc": "Landing con CTA, FAQ y «Por qué elegirnos»",
            "path": f"{base}/paso-3-web/index.html",
            "estado": "demo",
            "listo": True,
            "falta": "Deploy + GBP",
        },
        {
            "paso": 4,
            "slug": "paso-4-whatsapp",
            "nombre": "Bot WhatsApp",
            "desc": "Simulación agendar hora · demo sin API",
            "path": f"{base}/paso-4-whatsapp/index.html",
            "estado": "demo",
            "listo": True,
            "falta": "API Meta + webhook",
        },
    ]


def embudo_index_path() -> str:
    return "clientes/clinica-sol/proyectos/audit-inicial/entregables/index.html"


def scan_carpetas() -> list[dict]:
    skip = frozenset({".git", ".cursor", "vendor", "node_modules", "__pycache__", ".venv"})
    tipo_map = {
        "analisis-de-proyectos": "pipeline",
        "lluvia-de-ideas": "pipeline",
        "ideas de proyectos": "pipeline",
        "marketing-audit": "pipeline",
        "project_lens": "pipeline",
        "creador de contenido": "pipeline",
        "creador de prompts": "pipeline",
        "creador de skills": "pipeline",
        "libros a entender": "pipeline",
        "linkedin-ghostwriter": "pipeline",
        "centro de control prime": "pipeline",
        "clientes": "clientes",
        "proyectos-top3": "producto",
        "meta": "config",
    }
    out = []
    for p in sorted(CURSORPRIME.iterdir()):
        if not p.is_dir() or p.name.startswith(".") or p.name in skip:
            continue
        subs = sorted(
            c.name for c in p.iterdir() if c.is_dir() and not c.name.startswith(".") and c.name not in skip
        )[:12]
        has_cli = bool(list(p.glob("*_main.py")) or (p / "main.py").exists() or (p / "evaluar.py").exists())
        out.append(
            {
                "nombre": p.name,
                "path": p.name,
                "tipo": tipo_map.get(p.name, "otro"),
                "has_cli": has_cli,
                "subcarpetas": subs,
            }
        )
    return out


def clientes_scan() -> list[dict]:
    root = CURSORPRIME / "clientes"
    if not root.exists():
        return []
    out = []
    for p in sorted(root.iterdir()):
        if not p.is_dir() or p.name.startswith("_"):
            continue
        proyectos = []
        proj_root = p / "proyectos"
        if proj_root.exists():
            for pr in sorted(proj_root.iterdir()):
                if pr.is_dir():
                    ent = (pr / "entregables" / "index.html").exists()
                    proyectos.append({"slug": pr.name, "embudo": ent})
        out.append({"slug": p.name, "proyectos": proyectos})
    return out

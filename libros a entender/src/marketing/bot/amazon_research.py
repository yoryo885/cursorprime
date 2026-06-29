"""Bot de investigación: autocompletado Amazon + competidores."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from src.config import RESUMENES_DIR
from src.marketing.bot.browser import amazon_url, launch_context
from src.marketing.brief import MarketingBrief


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _queries_from_brief(brief: MarketingBrief) -> list[str]:
    rol = brief.audiencia_oficial or "profesional"
    rol_corto = rol.split()[0] if rol else "profesional"
    concepto = "pareto" if "pareto" in brief.libro_fuente.lower() else brief.slug
    queries = [
        f"{concepto} {rol_corto}",
        f"guía {concepto} {rol_corto}",
        f"aplicar {concepto} {rol}",
        f"productividad {rol_corto}",
    ]
    for term in brief.lexico_rol[:3]:
        queries.append(f"{term} {concepto}")
    if brief.semanas_plan:
        queries.append(f"{concepto} {brief.semanas_plan} semanas")
    return queries


def _load_queries(slug: str, brief: MarketingBrief | None = None) -> list[str]:
    kdp = RESUMENES_DIR / slug / "kdp"
    queries: list[str] = []

    if brief:
        queries.extend(_queries_from_brief(brief))

    intel_path = kdp / "audience_intelligence.json"
    if intel_path.exists():
        data = json.loads(intel_path.read_text(encoding="utf-8"))
        intent = data.get("audiencia", {}).get("intencion_busqueda", {})
        queries.extend(intent.get("consultas_amazon_sugeridas", [])[:8])

    mr_path = kdp / "market_research.json"
    if mr_path.exists():
        data = json.loads(mr_path.read_text(encoding="utf-8"))
        queries.extend(data.get("busquedas", [])[:6])

    if not queries:
        queries = [f"guía {slug}", f"productividad {slug}"]

    seen: set[str] = set()
    out: list[str] = []
    for q in queries:
        qn = re.sub(r"\s+", " ", q.strip().lower())
        if qn and qn not in seen:
            seen.add(qn)
            out.append(q.strip())
    return out[:10]


def _fetch_suggestions_api(query: str, mercado: str) -> list[str]:
    mkt = "771770" if mercado.upper() == "MX" else "44551"
    url = (
        "https://completion.amazon.com/search/complete?"
        + urllib.parse.urlencode({
            "search-alias": "stripbooks",
            "client": "amazon-search-ui",
            "mkt": mkt,
            "q": query,
        })
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        data = json.loads(raw)
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            return [str(s) for s in data[1][:8] if s]
    except Exception:
        pass
    return []


def _suggestions_from_page(page: Page, query: str, mercado: str) -> list[str]:
    page.goto(amazon_url(mercado), wait_until="domcontentloaded", timeout=30000)
    time.sleep(1)

    box = None
    for sel in (
        "#twotabsearchtextbox",
        "input[name='field-keywords']",
        "#nav-search-bar-form input[type='text']",
    ):
        loc = page.locator(sel).first
        if loc.count():
            box = loc
            break
    if not box:
        return []

    box.click()
    box.fill("")
    box.type(query, delay=60)
    time.sleep(1.2)

    found: list[str] = []
    for sel in (
        "#sac-suggestion-row-template .s-suggestion",
        ".autocomplete-results-container div",
        "[role='option']",
        ".s-suggestion",
    ):
        for item in page.locator(sel).all()[:10]:
            try:
                t = item.inner_text(timeout=500).strip()
                if t and t.lower() != query.lower() and t not in found:
                    found.append(t)
            except Exception:
                continue
        if found:
            break
    return found[:8]


def _scrape_search_results(page: Page, query: str, mercado: str) -> list[dict[str, Any]]:
    url = f"{amazon_url(mercado)}/s?k={urllib.parse.quote(query)}&i=stripbooks"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(1.5)

    items: list[dict[str, Any]] = []
    for card in page.locator("[data-asin]").all():
        if len(items) >= 5:
            break
        try:
            asin = card.get_attribute("data-asin") or ""
            if not asin or asin == " ":
                continue
            title = ""
            for sel in ("h2 a span", "h2 span", ".a-text-normal"):
                loc = card.locator(sel).first
                if loc.count():
                    title = loc.inner_text(timeout=800).strip()
                    if title:
                        break
            price = ""
            for sel in (".a-price .a-offscreen", ".a-color-price"):
                loc = card.locator(sel).first
                if loc.count():
                    price = loc.inner_text(timeout=500).strip()
                    if price:
                        break
            if title:
                items.append({
                    "asin": asin,
                    "titulo": title[:200],
                    "precio": price,
                    "busqueda_origen": query,
                })
        except Exception:
            continue
    return items


class AmazonResearchBot:
    def run(
        self,
        slug: str,
        *,
        brief: MarketingBrief | None = None,
        mercado: str = "MX",
        headless: bool = False,
    ) -> tuple[Path, Path]:
        kdp_dir = RESUMENES_DIR / slug / "kdp"
        kdp_dir.mkdir(parents=True, exist_ok=True)
        if brief and brief.ctx:
            mercados = brief.ctx.kdp_seed.get("mercados") or []
            if mercados:
                mercado = str(mercados[0])
        queries = _load_queries(slug, brief=brief)

        print(f"🔎 Amazon {mercado} — {len(queries)} consultas")
        all_suggestions: list[str] = []
        all_competitors: list[dict[str, Any]] = []
        seen_asin: set[str] = set()

        for q in queries:
            api_sug = _fetch_suggestions_api(q, mercado)
            all_suggestions.extend(api_sug)
            if api_sug:
                print(f"   · «{q}» → {len(api_sug)} sugerencias")

        pw, context = launch_context(headless=headless, mercado=mercado)
        try:
            page = context.pages[0] if context.pages else context.new_page()

            for q in queries[:6]:
                if not any(q.lower() in s.lower() for s in all_suggestions):
                    browser_sug = _suggestions_from_page(page, q, mercado)
                    all_suggestions.extend(browser_sug)
                    if browser_sug:
                        print(f"   · «{q}» → {len(browser_sug)} (navegador)")

            for q in queries[:3]:
                for item in _scrape_search_results(page, q, mercado):
                    if item["asin"] not in seen_asin:
                        seen_asin.add(item["asin"])
                        all_competitors.append(item)

        finally:
            context.close()
            pw.stop()

        seen_s: set[str] = set()
        sugerencias: list[str] = []
        for s in all_suggestions:
            sl = s.strip().lower()
            if sl and sl not in seen_s:
                seen_s.add(sl)
                sugerencias.append(s.strip())

        mr_path = kdp_dir / "market_research.json"
        comp_path = kdp_dir / "competitors.json"
        mr_path.write_text(
            json.dumps({
                "mercado": mercado,
                "fecha": _now_iso(),
                "notas": "Pipeline marketing — bot Amazon",
                "busquedas": queries,
                "sugerencias_autocompletado": sugerencias[:20],
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        comp_path.write_text(
            json.dumps({
                "mercado": mercado,
                "fecha": _now_iso(),
                "notas": "Pipeline marketing — bot Amazon",
                "items": all_competitors[:15],
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"   ✓ {len(sugerencias)} sugerencias · {len(all_competitors)} competidores")
        return mr_path, comp_path

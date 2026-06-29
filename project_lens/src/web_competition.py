"""Scrape competidores con Playwright — V1 web real (afinado)."""

from __future__ import annotations

import logging
import re
import statistics
from datetime import datetime, timezone
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_FILTERS = {
    "max_urls": 10,
    "precio_clp_min": 8_000,
    "precio_clp_max": 400_000,
    "usd_to_clp": 950,
    "excluir_outliers": True,
}

# Precios con contexto mensual/anual
PRICE_RE = re.compile(
    r"(?:"
    r"(?:CLP|USD|US\$|\$|€|EUR)\s*[\d]{1,3}(?:[.,\s][\d]{3})*(?:[.,][\d]{1,2})?"
    r"|[\d]{1,3}(?:[.,\s][\d]{3})+(?:[.,][\d]{1,2})?\s*(?:CLP|USD|/mes|mensual|month|mo|/mo)"
    r"|[\d]+(?:[.,][\d]{2})?\s*(?:USD|CLP)?\s*/\s*(?:mes|mo|month|año|year|yr|anual)"
    r"|\$\s*[\d]+(?:[.,][\d]{2})?"
    r")",
    re.IGNORECASE,
)

ANNUAL_RE = re.compile(r"(?:año|year|yr|anual|annual)", re.IGNORECASE)
MONTHLY_RE = re.compile(r"(?:/mes|mensual|month|/mo|\bmo\b|monthly)", re.IGNORECASE)

PRICING_SELECTORS = [
    "[class*='price' i]",
    "[class*='pricing' i]",
    "[data-price]",
    "[class*='plan' i]",
    "main",
    "article",
]


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def merge_filters(idea: dict, constitution: dict | None = None) -> dict:
    base = {**DEFAULT_FILTERS, **(constitution or {}).get("competition", {})}
    override = idea.get("competencia_filtros") or {}
    return {**base, **override}


def collect_urls(idea: dict, max_urls: int) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add(u: str) -> None:
        u = u.strip()
        if not u or u in seen:
            return
        if not u.startswith(("http://", "https://")):
            return
        seen.add(u)
        urls.append(u)

    for block in idea.get("competencia") or []:
        if isinstance(block, dict):
            add(block.get("url") or "")
        elif isinstance(block, str):
            add(block)

    for u in idea.get("urls_referencia") or []:
        add(u)

    return urls[:max_urls]


def _normalize_price(raw: str, usd_to_clp: int = 950) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    if not digits or len(digits) > 9:
        return None
    val = int(digits)
    upper = raw.upper()
    is_usd = any(x in upper for x in ("USD", "US$")) or ("$" in raw and "CLP" not in upper)
    is_annual = bool(ANNUAL_RE.search(raw))

    if is_usd or (val < 800 and "$" in raw):
        val = int(val * usd_to_clp)
    if is_annual:
        val = max(1, val // 12)

    return val


def _extract_prices_from_text(text: str, usd_to_clp: int, limit: int = 30) -> list[dict]:
    """Extrae precios con metadata de contexto."""
    found: list[dict] = []
    for m in PRICE_RE.finditer(text):
        raw = m.group(0)
        start = max(0, m.start() - 40)
        ctx = text[start : m.end() + 40]
        val = _normalize_price(raw, usd_to_clp)
        if not val:
            continue
        found.append(
            {
                "clp": val,
                "raw": raw.strip(),
                "mensual": bool(MONTHLY_RE.search(ctx)),
                "anual": bool(ANNUAL_RE.search(ctx)),
            }
        )
        if len(found) >= limit:
            break
    return found


def filter_prices(items: list[dict], filtros: dict) -> tuple[list[int], list[dict]]:
    """Filtra precios por rango SaaS mensual y outliers."""
    lo = int(filtros["precio_clp_min"])
    hi = int(filtros["precio_clp_max"])
    descartados: list[dict] = []
    candidatos: list[int] = []

    for it in items:
        v = it["clp"]
        if v < lo or v > hi:
            descartados.append({"valor": v, "razon": f"fuera de rango {lo}-{hi}", "raw": it.get("raw")})
            continue
        # Priorizar explícitamente mensuales; anual ya normalizado
        candidatos.append(v)

    if not candidatos:
        return [], descartados

    if not filtros.get("excluir_outliers") or len(candidatos) < 4:
        return sorted(set(candidatos)), descartados

    q1 = statistics.quantiles(candidatos, n=4)[0]
    q3 = statistics.quantiles(candidatos, n=4)[2]
    iqr = q3 - q1
    bound_lo = max(lo, q1 - 1.5 * iqr)
    bound_hi = min(hi, q3 + 1.5 * iqr)

    usados: list[int] = []
    for v in candidatos:
        if bound_lo <= v <= bound_hi:
            usados.append(v)
        else:
            descartados.append({"valor": v, "razon": "outlier IQR", "raw": None})

    return sorted(set(usados)), descartados


def _domain_name(url: str) -> str:
    host = urlparse(url).netloc or url
    return host.replace("www.", "")


def _page_pricing_text(page) -> str:
    chunks: list[str] = []
    for sel in PRICING_SELECTORS:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                for i in range(min(loc.count(), 8)):
                    t = loc.nth(i).inner_text(timeout=3000)
                    if t and len(t) > 20:
                        chunks.append(t[:4000])
        except Exception:
            continue
    if chunks:
        return "\n".join(chunks)[:12000]
    return page.inner_text("body")[:12000]


def scrape_competitor(url: str, filtros: dict, timeout_ms: int = 25000) -> dict:
    result = {
        "url": url,
        "nombre": _domain_name(url),
        "precios_detectados": [],
        "precios_filtrados": [],
        "precios_descartados": [],
        "snippet": "",
        "mock": True,
        "error": None,
    }
    if not _playwright_available():
        result["error"] = "playwright no instalado"
        return result

    try:
        from playwright.sync_api import sync_playwright

        usd = int(filtros.get("usd_to_clp", 950))
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            page.wait_for_timeout(800)
            title = page.title() or _domain_name(url)
            body = _page_pricing_text(page)
            browser.close()

        raw_items = _extract_prices_from_text(body, usd)
        crudos = sorted({it["clp"] for it in raw_items})
        filtrados, descartados = filter_prices(raw_items, filtros)

        result.update(
            {
                "nombre": title[:120],
                "precios_detectados": crudos,
                "precios_filtrados": filtrados,
                "precios_descartados": descartados,
                "snippet": " ".join(body.split())[:280],
                "mock": False,
            }
        )
    except Exception as exc:
        logger.warning("scrape %s: %s", url, exc)
        result["error"] = str(exc)[:200]
    return result


def _source(url: str, title: str, mock: bool) -> dict:
    return {
        "url": url,
        "title": title,
        "accessed_at": datetime.now(timezone.utc).isoformat(),
        "mock": mock,
    }


def _saturacion(n: int, prices: list[int]) -> str:
    if n >= 7:
        return "alta"
    if n >= 4:
        return "media"
    if n <= 2 and len(prices) >= 2:
        return "baja"
    return "media"


def fetch_competition(idea: dict, mock: bool = True, filters: dict | None = None) -> dict:
    filtros = merge_filters(idea, filters)
    max_urls = int(filtros["max_urls"])
    urls = collect_urls(idea, max_urls)

    if mock or not urls:
        n = max(2, min(8, len(urls) + 3))
        return {
            "num_competidores": n,
            "precio_min": 10000,
            "precio_max": 150000,
            "precio_mediana_clp": 80000,
            "saturacion": "media" if n < 6 else "alta",
            "competidores": [{"nombre": f"Competidor {i+1}", "url": "", "mock": True} for i in range(min(3, n))],
            "sources": [_source(u, "Referencia (mock)", True) for u in urls[:2]]
            or [_source("https://example.com/competitors", "Competencia (mock)", True)],
            "mock": True,
            "warnings": ["mock — añade urls_referencia y MOCK_WEB=false"] if not urls else ["mock activo"],
            "filtros_aplicados": filtros,
            "urls_procesadas": 0,
            "urls_solicitadas": len(urls),
        }

    if not _playwright_available():
        return {
            **fetch_competition({**idea, "urls_referencia": [], "competencia": []}, mock=True, filters=filters),
            "warnings": ["playwright no instalado — bash scripts/setup_web.sh"],
            "mock": True,
        }

    competidores = []
    all_prices: list[int] = []
    all_descartados: list[dict] = []
    sources = []
    warnings: list[str] = []

    for url in urls:
        c = scrape_competitor(url, filtros)
        competidores.append(c)
        sources.append(_source(url, c["nombre"], not c.get("error")))
        usados = c.get("precios_filtrados") or []
        all_prices.extend(usados)
        all_descartados.extend(c.get("precios_descartados") or [])
        if c.get("error"):
            warnings.append(f"{_domain_name(url)}: {c['error']}")
        elif not usados and c.get("precios_detectados"):
            warnings.append(f"{_domain_name(url)}: {len(c['precios_detectados'])} precios crudos, 0 pasaron filtros")

    real_count = sum(1 for c in competidores if not c.get("error"))
    n = len(competidores)

    if all_prices:
        precio_min, precio_max = min(all_prices), max(all_prices)
        mediana = int(statistics.median(all_prices))
    else:
        precio_min, precio_max, mediana = int(filtros["precio_clp_min"]), int(filtros["precio_clp_max"]), 80000
        warnings.append(
            f"ningún precio en rango {filtros['precio_clp_min']}-{filtros['precio_clp_max']} CLP/mes — revisa filtros o URLs"
        )

    saturacion = _saturacion(n, all_prices)
    any_mock = real_count < n or not all_prices

    return {
        "num_competidores": n,
        "precio_min": precio_min,
        "precio_max": precio_max,
        "precio_mediana_clp": mediana,
        "saturacion": saturacion,
        "competidores": competidores,
        "sources": sources,
        "mock": any_mock,
        "warnings": warnings,
        "precios_totales_detectados": sum(len(c.get("precios_detectados") or []) for c in competidores),
        "precios_usados": len(all_prices),
        "precios_descartados_total": len(all_descartados),
        "filtros_aplicados": filtros,
        "urls_procesadas": n,
        "urls_solicitadas": len(urls),
    }

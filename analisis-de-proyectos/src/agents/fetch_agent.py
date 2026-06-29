"""Búsqueda YouTube + web — live (DuckDuckGo) o mock."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import (
    FETCH_FALLBACK_MOCK,
    MAX_RESULTADOS_WEB,
    MAX_RESULTADOS_YT,
    MOCK_FETCH,
    load_json,
    save_json,
)
from src.types import AgentResult, PipelineContext

MOCK_YOUTUBE = [
    {
        "titulo": "Cómo publicar resúmenes de libros en Amazon KDP (paso a paso)",
        "url": "https://www.youtube.com/watch?v=mock-kdp-1",
        "snippet": "Tutorial sobre nichos de no-ficción, portadas y listings optimizados.",
        "fuente": "youtube",
    },
    {
        "titulo": "Faceless channel: resúmenes de libros con IA — ¿sigue funcionando?",
        "url": "https://www.youtube.com/watch?v=mock-kdp-2",
        "snippet": "Análisis de canales que resumen bestsellers y monetizan con ebooks.",
        "fuente": "youtube",
    },
    {
        "titulo": "Automatizar ebooks KDP con ChatGPT y Canva",
        "url": "https://www.youtube.com/watch?v=mock-kdp-3",
        "snippet": "Pipeline manual: investigación → guion → diseño → publicación.",
        "fuente": "youtube",
    },
]

MOCK_WEB = [
    {
        "titulo": "Amazon KDP low content books trends",
        "url": "https://example.com/kdp-trends",
        "snippet": "Guías prácticas y resúmenes por profesión siguen en nichos long-tail.",
        "fuente": "web",
    },
    {
        "titulo": "Self publishing forum — book summary niche",
        "url": "https://example.com/forum",
        "snippet": "Autores venden sistemas + plantillas además del ebook suelto.",
        "fuente": "web",
    },
]


def _search_ddg(query: str, max_results: int, fuente: str) -> list[dict]:
    """DuckDuckGo — prueba paquete `ddgs` y fallback `duckduckgo_search`."""
    last_err: str | None = None

    def _run(ddgs_factory) -> list[dict]:
        out: list[dict] = []
        with ddgs_factory() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                url = r.get("href") or r.get("url") or ""
                if not url:
                    continue
                detected = "youtube" if "youtube.com" in url or "youtu.be" in url else fuente
                out.append(
                    {
                        "titulo": (r.get("title") or "")[:200],
                        "url": url,
                        "snippet": (r.get("body") or r.get("snippet") or "")[:400],
                        "fuente": detected,
                    }
                )
        return out

    for attempt in range(2):
        for label, factory in _ddg_backends():
            try:
                results = _run(factory)
                if results:
                    return results
            except Exception as exc:
                last_err = f"{label}: {exc}"
    if not _ddg_backends():
        raise RuntimeError("Instala: pip install ddgs  (o duckduckgo-search)")
    if last_err:
        raise RuntimeError(f"Búsqueda falló — {last_err}")
    return []


def _ddg_backends() -> list[tuple[str, type]]:
    try:
        from ddgs import DDGS as DDGSNew

        return [("ddgs", DDGSNew)]
    except ImportError:
        pass
    try:
        from duckduckgo_search import DDGS as DDGSOld

        return [("duckduckgo_search", DDGSOld)]
    except ImportError:
        pass
    return []


def _dedupe(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for it in items:
        u = it.get("url") or ""
        if u and u not in seen:
            seen.add(u)
            out.append(it)
    return out


def fetch_live(queries: list[str]) -> tuple[list[dict], list[dict], list[str]]:
    """Busca en vivo. Devuelve youtube, web, warnings."""
    youtube: list[dict] = []
    web: list[dict] = []
    warnings: list[str] = []

    if not queries:
        warnings.append("Sin queries — usa --texto o brief con queries")
        return youtube, web, warnings

    for q in queries:
        yt_q = q if "youtube" in q.lower() else f"{q} site:youtube.com"
        try:
            youtube.extend(_search_ddg(yt_q, MAX_RESULTADOS_YT, "youtube"))
        except RuntimeError as exc:
            warnings.append(f"YouTube «{q[:40]}»: {exc}")

        try:
            web.extend(_search_ddg(q, MAX_RESULTADOS_WEB, "web"))
        except RuntimeError as exc:
            warnings.append(f"Web «{q[:40]}»: {exc}")

    youtube = _dedupe(youtube)[:MAX_RESULTADOS_YT]
    web = _dedupe([w for w in _dedupe(web) if w.get("fuente") != "youtube"])[:MAX_RESULTADOS_WEB]
    return youtube, web, warnings


class FetchAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        queries = context.get("queries") or []
        warnings: list[str] = []

        if MOCK_FETCH:
            youtube = MOCK_YOUTUBE
            web = MOCK_WEB
            mode = "mock"
        else:
            youtube, web, warnings = fetch_live(queries)
            mode = "live"
            if not youtube and not web:
                if FETCH_FALLBACK_MOCK:
                    youtube = MOCK_YOUTUBE
                    web = MOCK_WEB
                    mode = "mock_fallback"
                    warnings.append("Live sin resultados — usando mock de respaldo")
                else:
                    return AgentResult(
                        ok=False,
                        notes="Fetch live sin resultados — revisa red, queries o rate limit DDG",
                        warnings=warnings,
                    )

        payload = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "mock": MOCK_FETCH,
            "mode": mode,
            "queries_usadas": queries,
            "youtube": youtube,
            "web": web,
            "total": len(youtube) + len(web),
            "warnings": warnings,
        }
        save_json(ctx.paths["fetch"], payload)

        note = f"{payload['total']} resultados ({mode})"
        if warnings:
            note += f" · {len(warnings)} aviso(s)"
        return AgentResult(
            ok=payload["total"] > 0,
            artifacts=[str(ctx.paths["fetch"])],
            notes=note,
            warnings=warnings,
        )

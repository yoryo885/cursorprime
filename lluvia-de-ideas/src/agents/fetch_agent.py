"""Agente: busca en YouTube (vía DDG) y web."""

from __future__ import annotations

from datetime import datetime, timezone

from src.config import MAX_RESULTADOS_WEB, MAX_RESULTADOS_YT, MOCK_FETCH, load_json, save_json
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


def _search_ddg(query: str, max_results: int) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return []

    out: list[dict] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                out.append(
                    {
                        "titulo": r.get("title") or "",
                        "url": r.get("href") or "",
                        "snippet": r.get("body") or "",
                        "fuente": "youtube" if "youtube.com" in (r.get("href") or "") else "web",
                    }
                )
    except Exception:
        return []
    return out


class FetchAgent:
    def run(self, ctx: PipelineContext) -> AgentResult:
        context = load_json(ctx.paths["context"], {})
        queries = context.get("queries") or []
        youtube: list[dict] = []
        web: list[dict] = []

        if MOCK_FETCH:
            youtube = MOCK_YOUTUBE
            web = MOCK_WEB
        else:
            for q in queries:
                yt_q = q if "youtube" in q.lower() else f"{q} site:youtube.com"
                youtube.extend(_search_ddg(yt_q, MAX_RESULTADOS_YT))
                web.extend(_search_ddg(q, MAX_RESULTADOS_WEB))

        # dedupe by url
        seen: set[str] = set()
        def uniq(items: list[dict]) -> list[dict]:
            result = []
            for it in items:
                u = it.get("url") or ""
                if u and u not in seen:
                    seen.add(u)
                    result.append(it)
            return result

        payload = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "mock": MOCK_FETCH,
            "youtube": uniq(youtube)[:MAX_RESULTADOS_YT],
            "web": uniq(web)[:MAX_RESULTADOS_WEB],
            "total": 0,
        }
        payload["total"] = len(payload["youtube"]) + len(payload["web"])
        save_json(ctx.paths["fetch"], payload)

        mode = "mock" if MOCK_FETCH else "live"
        return AgentResult(
            ok=payload["total"] > 0,
            artifacts=[str(ctx.paths["fetch"])],
            notes=f"{payload['total']} resultados ({mode})",
            warnings=[] if payload["total"] else ["Sin resultados — revisa MOCK_FETCH o red"],
        )

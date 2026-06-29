"""Fetch y análisis HTML — wrapper sobre vendor analyze_page."""

from __future__ import annotations

import sys
from urllib.parse import urlparse

from src.config import MOCK_FETCH, VENDOR_ROOT

MOCK_PAGE = {
    "url": "https://demo.example.com",
    "analysis": {
        "seo": {
            "title": "Demo Business — Automatización para PYMEs",
            "meta_description": "",
            "headings": {"h1": ["Automatiza tu negocio hoy"], "h2": ["Features", "Pricing"]},
            "has_viewport": True,
            "images_without_alt": 3,
        },
        "conversion": {
            "cta_count": 2,
            "ctas": [{"text": "Start free trial", "href": "/signup"}],
            "form_count": 1,
            "forms": [{"fields": 4}],
        },
        "trust": {"social_link_count": 2},
        "tracking": {"schema_count": 0, "tools_count": 1},
        "scores": {"seo": 6, "cta": 7, "trust": 6, "tracking": 5},
        "overall_score": 6.0,
        "word_count": 850,
    },
}


def _import_analyze():
    scripts = VENDOR_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from analyze_page import analyze  # noqa: WPS433

    return analyze


def fetch_and_analyze(url: str) -> dict:
    if not url.startswith("http"):
        url = f"https://{url}"

    if MOCK_FETCH:
        data = {**MOCK_PAGE, "url": url, "mock": True}
        return data

    try:
        analyze = _import_analyze()
        result = analyze(url)
        result["mock"] = False
        return result
    except Exception as exc:
        data = {**MOCK_PAGE, "url": url, "mock": True, "fetch_error": str(exc)}
        return data


def detect_business_type(url: str, analysis: dict) -> str:
    text = " ".join(
        [
            analysis.get("analysis", {}).get("seo", {}).get("title", ""),
            url.lower(),
        ]
    ).lower()
    if any(k in text for k in ("shop", "cart", "product", "store")):
        return "e-commerce"
    if any(k in text for k in ("pricing", "trial", "saas", "api", "login")):
        return "saas"
    if any(k in text for k in ("clinic", "spa", "dental", "med")):
        return "local_business"
    if any(k in text for k in ("agency", "portfolio", "case study")):
        return "agency"
    return "general"


def domain_from_url(url: str) -> str:
    return urlparse(url if "://" in url else f"https://{url}").netloc.replace("www.", "")

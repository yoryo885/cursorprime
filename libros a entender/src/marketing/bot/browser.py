"""Playwright — navegador persistente para Amazon/KDP."""
from __future__ import annotations

from playwright.sync_api import BrowserContext, Playwright, sync_playwright

from src.config import BASE_DIR

PROFILE_DIR = BASE_DIR / ".cache" / "amazon_bot" / "profile"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

AMAZON_BASE = {
    "MX": "https://www.amazon.com.mx",
    "ES": "https://www.amazon.es",
}


def amazon_url(mercado: str = "MX") -> str:
    return AMAZON_BASE.get(mercado.upper(), AMAZON_BASE["MX"])


def launch_context(
    *,
    headless: bool = False,
    mercado: str = "MX",
) -> tuple[Playwright, BrowserContext]:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    pw = sync_playwright().start()
    locale = "es-MX" if mercado.upper() == "MX" else "es-ES"
    context = pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        locale=locale,
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    return pw, context

"""13 — Visual QA con Playwright (screenshots + overlap real)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def run(input: dict[str, Any]) -> dict[str, Any]:
    """
    Abre landing.html, screenshots mobile/desktop, chequea overlap de sections.
    Si Playwright no está: skipped=True (no rompe el pipeline).
    """
    html_path = Path(input.get("html_path") or "")
    out_dir = Path(input.get("out_dir") or html_path.parent)
    shots = out_dir / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "skipped": False,
        "motivo": "",
        "screenshots": {},
        "overlaps": [],
        "ok": True,
    }

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result["skipped"] = True
        result["motivo"] = "Playwright no instalado (pip install playwright && playwright install chromium)"
        return result

    if not html_path.exists():
        result["skipped"] = True
        result["motivo"] = f"No existe {html_path}"
        return result

    uri = html_path.resolve().as_uri()
    mobile_path = shots / "mobile.png"
    desktop_path = shots / "desktop.png"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Desktop
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(uri, wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(desktop_path), full_page=True)
            overlaps = page.evaluate(
                """() => {
                  const sections = Array.from(document.querySelectorAll('section'));
                  const boxes = sections.map((el, i) => {
                    const r = el.getBoundingClientRect();
                    const top = r.top + window.scrollY;
                    return { i, id: el.id || ('section-'+i), top, bottom: top + r.height, height: r.height };
                  });
                  const overlaps = [];
                  for (let i = 1; i < boxes.length; i++) {
                    const prev = boxes[i-1], cur = boxes[i];
                    if (cur.top < prev.bottom - 1) {
                      overlaps.push({
                        a: prev.id, b: cur.id,
                        overlap_px: Math.round(prev.bottom - cur.top)
                      });
                    }
                  }
                  return overlaps;
                }"""
            )
            result["overlaps"] = overlaps

            # Mobile
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(uri, wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(mobile_path), full_page=True)
            browser.close()
    except Exception as e:
        result["skipped"] = True
        result["motivo"] = f"Playwright error: {e}"
        return result

    result["screenshots"] = {
        "mobile": str(mobile_path),
        "desktop": str(desktop_path),
    }
    result["ok"] = len(result["overlaps"]) == 0
    return result

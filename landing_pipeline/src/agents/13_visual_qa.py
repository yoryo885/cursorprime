"""13 — Visual QA: screenshots + overlap + detección animaciones."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def run(input: dict[str, Any]) -> dict[str, Any]:
    html_path = Path(input.get("html_path") or "")
    out_dir = Path(input.get("out_dir") or html_path.parent)
    shots = out_dir / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "skipped": False,
        "motivo": "",
        "screenshots": {},
        "scroll_shots": [],
        "overlaps": [],
        "animation_risks": [],
        "ok": True,
    }

    html = ""
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        risks = []
        if re.search(r"IntersectionObserver", html):
            risks.append("IntersectionObserver")
        if re.search(r"fade-in-up|scroll-reveal|reveal-on-scroll", html, re.I):
            risks.append("reveal-class")
        if re.search(r"opacity\s*:\s*0", html) and re.search(r"translateY\s*\(", html):
            risks.append("opacity0+translateY")
        result["animation_risks"] = risks

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result["skipped"] = True
        result["motivo"] = "Playwright no instalado"
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
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(uri, wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(desktop_path), full_page=True)

            overlaps = page.evaluate(
                """() => {
                  const sections = Array.from(document.querySelectorAll('[data-section], section'));
                  const boxes = sections.map((el, i) => {
                    const r = el.getBoundingClientRect();
                    const top = r.top + window.scrollY;
                    return { id: el.getAttribute('data-section') || el.id || ('s'+i), top, bottom: top + r.height };
                  });
                  const overlaps = [];
                  for (let i = 1; i < boxes.length; i++) {
                    const prev = boxes[i-1], cur = boxes[i];
                    if (cur.top < prev.bottom - 1) {
                      overlaps.push({ a: prev.id, b: cur.id, overlap_px: Math.round(prev.bottom - cur.top) });
                    }
                  }
                  return overlaps;
                }"""
            )
            result["overlaps"] = overlaps

            # Scroll incremental + screenshots
            height = page.evaluate("() => document.body.scrollHeight")
            scroll_dir = shots / "scroll"
            scroll_dir.mkdir(exist_ok=True)
            scroll_shots = []
            step = 400
            y = 0
            idx = 0
            while y < height and idx < 8:
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(150)
                path = scroll_dir / f"scroll_{idx:02d}.png"
                page.screenshot(path=str(path))
                scroll_shots.append(str(path))
                # overlap mid-scroll
                mid = page.evaluate(
                    """() => {
                      const sections = Array.from(document.querySelectorAll('[data-section]'));
                      const overlaps = [];
                      for (let i = 1; i < sections.length; i++) {
                        const a = sections[i-1].getBoundingClientRect();
                        const b = sections[i].getBoundingClientRect();
                        if (b.top < a.bottom - 1 && b.bottom > a.top) {
                          const ov = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
                          if (ov > 2) overlaps.push({a: sections[i-1].dataset.section, b: sections[i].dataset.section, overlap_px: Math.round(ov)});
                        }
                      }
                      return overlaps;
                    }"""
                )
                for o in mid:
                    if o not in result["overlaps"]:
                        result["overlaps"].append(o)
                y += step
                idx += 1
            result["scroll_shots"] = scroll_shots

            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(uri, wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(mobile_path), full_page=True)
            browser.close()
    except Exception as e:
        result["skipped"] = True
        result["motivo"] = f"Playwright error: {e}"
        return result

    result["screenshots"] = {"mobile": str(mobile_path), "desktop": str(desktop_path)}
    result["ok"] = len(result["overlaps"]) == 0 and not result["animation_risks"]
    return result

"""Asistente KDP: navegador + panel copiar listing."""
from __future__ import annotations

import html
import json
import webbrowser
from pathlib import Path

from src.config import RESUMENES_DIR
from src.marketing.bot.browser import launch_context


def _load_listing(slug: str) -> dict:
    path = RESUMENES_DIR / slug / "kdp" / "amazon_listing.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No hay listing en {path}. Ejecuta: python kdp_main.py --slug {slug}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _build_helper_html(listing: dict, slug: str) -> str:
    titulo = html.escape(listing.get("titulo") or "")
    subtitulo = html.escape(listing.get("subtitulo") or "")
    desc = listing.get("descripcion_html") or ""
    keywords = listing.get("keywords") or []
    kw_lines = "\\n".join(html.escape(k) for k in keywords)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>KDP Assistant — {html.escape(slug)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 24px auto; padding: 0 16px; }}
    h1 {{ font-size: 1.25rem; }}
    section {{ margin: 20px 0; padding: 16px; border: 1px solid #ddd; border-radius: 8px; }}
    button {{ margin-top: 8px; padding: 8px 14px; cursor: pointer; }}
    pre, textarea {{ white-space: pre-wrap; word-break: break-word; background: #f6f6f6; padding: 12px; }}
    textarea {{ width: 100%; min-height: 120px; }}
    .ok {{ color: green; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Asistente KDP — {html.escape(slug)}</h1>
  <p>Abre <a href="https://kdp.amazon.com" target="_blank">kdp.amazon.com</a>. Usa los botones para copiar.</p>

  <section>
    <h2>Título ({len(listing.get("titulo") or "")} chars)</h2>
    <pre id="titulo">{titulo}</pre>
    <button onclick="copy('titulo')">Copiar título</button>
    <span id="ok-titulo" class="ok"></span>
  </section>

  <section>
    <h2>Subtítulo</h2>
    <pre id="subtitulo">{subtitulo}</pre>
    <button onclick="copy('subtitulo')">Copiar subtítulo</button>
  </section>

  <section>
    <h2>Descripción HTML</h2>
    <textarea id="descripcion" readonly></textarea>
    <button onclick="copy('descripcion')">Copiar descripción</button>
  </section>

  <section>
    <h2>Keywords (7)</h2>
    <pre id="keywords">{kw_lines}</pre>
    <button onclick="copy('keywords')">Copiar keywords</button>
  </section>

  <script>
    document.getElementById("descripcion").value = {json.dumps(desc)};
    function copy(id) {{
      const el = document.getElementById(id);
      const text = el.value !== undefined ? el.value : el.innerText;
      navigator.clipboard.writeText(text).then(() => {{
        const ok = document.getElementById("ok-" + id);
        if (ok) ok.textContent = "✓ Copiado";
        setTimeout(() => {{ if (ok) ok.textContent = ""; }}, 2000);
      }});
    }}
  </script>
</body>
</html>
"""


class KDPAssistantBot:
    def run(self, slug: str) -> Path:
        listing = _load_listing(slug)
        kdp_dir = RESUMENES_DIR / slug / "kdp"
        helper = kdp_dir / "kdp_assistant.html"
        helper.write_text(_build_helper_html(listing, slug), encoding="utf-8")

        print(f"📋 Panel: {helper}")
        webbrowser.open(helper.as_uri())

        print("🌐 Abriendo KDP...")
        pw, context = launch_context(headless=False)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://kdp.amazon.com/", wait_until="domcontentloaded", timeout=60000)
            print("✓ KDP abierto. Copia campos desde el panel.")
            input("\n[Enter] para cerrar...")
        finally:
            context.close()
            pw.stop()

        return helper

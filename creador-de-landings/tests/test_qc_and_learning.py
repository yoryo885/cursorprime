"""QC 1-producto + efectos de aprendizaje."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.learning import _parse_efectos, aplicar_al_brief  # noqa: E402
from src.templates.html_builder import build_html  # noqa: E402


class TestLearningEffects(unittest.TestCase):
    def test_parse_ocultar_newsletter(self) -> None:
        e = _parse_efectos("quiero quitar newsletter", "ocultar bloque")
        self.assertTrue(e.get("ocultar_newsletter"))

    def test_aplicar_oculta_en_html(self) -> None:
        brief = {
            "marca": "Test",
            "producto": "P",
            "promesa": "Hola",
            "cta": "Comprar",
            "estilo": "tienda",
            "productos": [
                {
                    "titulo": "Guía",
                    "rol": "coach",
                    "libro": "norte",
                    "precio": "$1",
                    "disponible": True,
                }
            ],
            "roles": [{"slug": "coach", "nombre": "Coach"}],
            "serie_libros": [{"slug": "norte", "titulo": "Libro", "autor": "A"}],
            "historia": "Historia",
            "mision": "Misión",
            "hero_badge_calidad": "Badge",
            "precio": "$1",
            "incluye": ["A", "B"],
            "calidad": [{"titulo": "Q", "texto": "T"}],
            "faq": [{"q": "¿?", "a": "Sí"}],
            "barra_aviso": "Aviso",
            "ocultar_newsletter": True,
        }
        html = build_html(brief)
        self.assertNotIn('id="newsletter"', html)
        self.assertIn("hero-badge", html)
        self.assertIn("class=\"incluye\"", html)


class TestQcOneProduct(unittest.TestCase):
    def test_one_product_catalog_ok(self) -> None:
        from src.agents.qc_agent import QcAgent
        from src.types import PipelineContext

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            preview = td_path / "preview.html"
            brief_path = td_path / "brief.json"
            qc_path = td_path / "qc.json"
            brief = {
                "marca": "Norte",
                "promesa": "Plan claro",
                "cta": "Comprar",
                "estilo": "tienda",
                "mostrar_catalogo": True,
                "productos": [{"titulo": "Una"}],
            }
            html = (
                "<!DOCTYPE html><html><body>"
                + ("<!-- pad -->" * 40)
                + '<div class="brand-hero">Norte</div>'
                '<section class="hero-nuevo"><h1>Hero</h1></section>'
                '<a class="btn" href="#">Comprar</a><div id="guias"></div>'
                "</body></html>"
            )
            preview.write_text(html, encoding="utf-8")
            brief_path.write_text(__import__("json").dumps(brief), encoding="utf-8")
            ctx = PipelineContext(
                slug="t",
                paths={"preview": preview, "brief": brief_path, "qc": qc_path},
                respuestas={},
                constitution={
                    "qc_minimo": {
                        "tiene_marca": True,
                        "tiene_headline": True,
                        "tiene_cta": True,
                        "tiene_hero_visual": True,
                        "archivo_html": True,
                    }
                },
                ejemplo="tienda",
            )
            result = QcAgent().run(ctx)
            self.assertTrue(result.ok, result.notes)


if __name__ == "__main__":
    unittest.main()

"""Smoke: contrato Brief ↔ copy_profesional (keys requeridas)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.copy_marketing import copy_profesional  # noqa: E402

REQUIRED_KEYS = {
    "barra_aviso",
    "promesa",
    "hero_eyebrow",
    "hero_titulo",
    "hero_sub",
    "hero_badge_calidad",
    "catalogo_titulo",
    "catalogo_sub",
    "serie_titulo",
    "serie_sub",
    "calidad_titulo",
    "calidad",
    "incluye_titulo",
    "incluye",
    "historia",
    "mision",
    "beneficios",
    "faq",
    "newsletter_titulo",
    "newsletter_sub",
    "newsletter_cta",
    "social_proof_nota",
}


class TestBriefCopyContract(unittest.TestCase):
    def test_copy_profesional_has_required_keys(self) -> None:
        copy = copy_profesional("Vértice Pro", 6, 5, "desde $4.99")
        missing = REQUIRED_KEYS - set(copy.keys())
        self.assertEqual(missing, set(), f"Faltan keys en copy_profesional: {missing}")
        self.assertTrue(str(copy["hero_badge_calidad"]).strip())


if __name__ == "__main__":
    unittest.main()

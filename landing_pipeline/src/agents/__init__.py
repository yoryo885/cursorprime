"""Carga agentes 01–12 (nombres con dígitos vía importlib)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

_DIR = Path(__file__).resolve().parent


def _load(name: str) -> ModuleType:
    path = _DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"landing_agents.{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se puede cargar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


a01_brief = _load("01_brief")
a02_hero = _load("02_hero")
a03_social_proof = _load("03_social_proof")
a04_problem = _load("04_problem")
a05_benefits = _load("05_benefits")
a06_testimonials = _load("06_testimonials")
a07_pricing = _load("07_pricing")
a08_faq = _load("08_faq")
a09_cta_final = _load("09_cta_final")
a10_footer = _load("10_footer")
a11_design = _load("11_design")
a12_qa = _load("12_qa")

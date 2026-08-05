"""Variantes de template por sección (lista cerrada)."""

SECTION_ORDER = [
    "hero",
    "social_proof",
    "problem",
    "benefits",
    "testimonials",
    "pricing",
    "faq",
    "cta_final",
    "footer",
]

# Variantes permitidas — el LLM solo elige nombres de esta lista
LAYOUT_VARIANTS = {
    "hero": ["centrado", "split"],
    "benefits": ["tarjetas", "lista_numerada"],
    "pricing": ["una_columna", "comparativa"],
}

LAYOUT_DEFAULTS = {
    "hero": "centrado",
    "benefits": "tarjetas",
    "pricing": "una_columna",
}

# sec → variante → archivo
SECTION_TEMPLATES = {
    "hero": {
        "centrado": "hero_centrado.html",
        "split": "hero_split.html",
    },
    "social_proof": {"default": "social_proof.html"},
    "problem": {"default": "problem.html"},
    "benefits": {
        "tarjetas": "benefits_tarjetas.html",
        "lista_numerada": "benefits_lista_numerada.html",
    },
    "testimonials": {"default": "testimonials.html"},
    "pricing": {
        "una_columna": "pricing_una_columna.html",
        "comparativa": "pricing_comparativa.html",
    },
    "faq": {"default": "faq.html"},
    "cta_final": {"default": "cta_final.html"},
    "footer": {"default": "footer.html"},
}


def resolve_template(sec: str, layout: dict) -> str:
    variants = SECTION_TEMPLATES.get(sec) or {}
    if "default" in variants and len(variants) == 1:
        return variants["default"]
    chosen = (layout or {}).get(sec) or LAYOUT_DEFAULTS.get(sec)
    if chosen not in variants:
        chosen = LAYOUT_DEFAULTS.get(sec) or next(iter(variants))
    return variants[chosen]

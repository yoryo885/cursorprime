"""Orden fijo de secciones — cada una se renderiza exactamente una vez."""

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

# Mapeo copy.json key → template
SECTION_TEMPLATE = {
    "hero": "hero.html",
    "social_proof": "social_proof.html",
    "problem": "problem.html",
    "benefits": "benefits.html",
    "testimonials": "testimonials.html",
    "pricing": "pricing.html",
    "faq": "faq.html",
    "cta_final": "cta_final.html",
    "footer": "footer.html",
}

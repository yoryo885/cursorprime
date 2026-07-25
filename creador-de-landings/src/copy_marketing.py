"""Copy profesional de marketing para landings (tono editorial / calidad)."""

from __future__ import annotations


def copy_profesional(marca: str, n_productos: int, n_roles: int, precio: str = "") -> dict:
    """Bloques de texto listos para brief + HTML. Sin testimonios inventados."""
    precio_line = precio or "desde $4.99"
    return {
        "barra_aviso": (
            f"Colección profesional · PDF de alta calidad · descarga inmediata · {precio_line}"
        ),
        "promesa": "Métodos de libros clásicos, aplicados a tu oficio — con la calidad de una guía profesional",
        "hero_eyebrow": "Colección profesional",
        "hero_titulo": f"Guías libro × rol para profesionales",
        "hero_sub": (
            f"{n_productos} guías · {n_roles} oficios · métodos de libros clásicos aplicados a tu trabajo."
        ),
        "hero_badge_calidad": (
            "Edición profesional · plan 10 semanas · listo para usar"
        ),
        "catalogo_titulo": "Explora la colección",
        "catalogo_sub": (
            f"{n_productos} guías · {n_roles} roles · elige la combinación que necesitas hoy "
            "y reserva aviso para las que vienen."
        ),
        "serie_titulo": "Basadas en libros que ya funcionan",
        "serie_sub": "Cada guía toma un libro de referencia y lo traduce a tu realidad laboral.",
        "calidad_titulo": "Por qué la calidad importa",
        "calidad": [
            {
                "titulo": "Hecha para tu oficio",
                "texto": "Ejemplos, lenguaje y prioridades de tu rol — no teoría genérica.",
            },
            {
                "titulo": "Método claro en 10 semanas",
                "texto": "Plan semanal accionable: sabes qué hacer cada semana, sin relleno.",
            },
            {
                "titulo": "Formato profesional",
                "texto": "PDF editable en la práctica diaria: denso, ordenado y listo para imprimir o digital.",
            },
            {
                "titulo": "Colección que crece",
                "texto": "Más libros × más roles. Empiezas con una guía y amplías cuando lo necesites.",
            },
        ],
        "incluye_titulo": "Qué incluye cada guía",
        "incluye": [
            "Marco del libro aplicado a tu rol",
            "Plan de acción de 10 semanas",
            "Checklist y prioridades 80/20",
            "Descarga inmediata en PDF",
        ],
        "historia": (
            f"{marca} convierte ideas de libros clásicos en herramientas de trabajo real. "
            "Diseñamos cada guía con criterio editorial: precisión, utilidad y respeto por tu tiempo. "
            "La colección cubre varios oficios — psicopedagogía, derecho, educación, salud y más — "
            "para que elijas la que habla tu lenguaje."
        ),
        "mision": (
            "Creemos que el conocimiento útil debe llegar al oficio, no quedarse en el estante. "
            "Por eso cada guía une un libro de referencia con un plan práctico para profesionales "
            "que quieren mejorar con método, no con moda."
        ),
        "beneficios": [
            "Colección multiproducto: varias guías libro × rol, no un único PDF",
            "Calidad editorial: estructura clara, sin relleno, lista para aplicar",
            "Enfocada en tu oficio: ejemplos y prioridades de tu día a día",
            "Plan de 10 semanas con avance medible",
            "Precio accesible de entrada profesional",
            "Nuevas combinaciones en camino — avísame cuando salgan",
        ],
        "faq": [
            {
                "q": "¿Solo venden una guía?",
                "a": "No. Ofrecemos una colección de guías (libro × rol). Algunas ya están disponibles y otras se lanzan pronto; puedes filtrar por oficio.",
            },
            {
                "q": "¿En qué se diferencia de un resumen genérico?",
                "a": "Cada guía está escrita para un rol concreto: lenguaje, ejemplos y plan de 10 semanas pensados para tu práctica profesional.",
            },
            {
                "q": "¿Qué calidad puedo esperar?",
                "a": "Edición profesional: estructura clara, método accionable y PDF listo para usar en el trabajo o estudio. Sin relleno.",
            },
            {
                "q": "¿Puedo comprar más de una?",
                "a": "Sí. La colección está pensada para ampliar: empieza por tu rol y suma otras guías cuando las necesites.",
            },
            {
                "q": "¿Cómo la recibo?",
                "a": "Descarga inmediata en PDF tras la compra. Sin esperas ni envíos físicos.",
            },
            {
                "q": "¿Hay más productos próximamente?",
                "a": "Sí. Seguimos abriendo combinaciones libro × rol. Usa “Avísame” en las guías próximas o el newsletter.",
            },
        ],
        "newsletter_titulo": "Acceso anticipado a nuevas guías",
        "newsletter_sub": (
            "Te avisamos cuando salga tu rol o libro. Sin spam: solo lanzamientos de la colección."
        ),
        "newsletter_cta": "Quiero avisos de la colección",
        "social_proof_nota": (
            "Las reseñas reales de clientes aparecerán aquí. No publicamos testimonios inventados."
        ),
    }


def enriquecer_productos(productos: list[dict], serie: list[dict]) -> list[dict]:
    """Añade subtítulo de marketing a cada guía del catálogo."""
    libros = {s.get("slug"): s for s in serie}
    out = []
    for p in productos:
        item = dict(p)
        libro = libros.get(p.get("libro"), {})
        autor = libro.get("autor") or ""
        titulo_libro = libro.get("titulo") or p.get("libro")
        if p.get("disponible"):
            item["subtitulo"] = (
                f"Basada en {titulo_libro}"
                + (f" · {autor}" if autor else "")
                + " · Edición profesional · Plan 10 semanas"
            )
            item["badge_marketing"] = "Disponible ahora"
        else:
            item["subtitulo"] = (
                f"Próximo lanzamiento · {titulo_libro}"
                + (f" · {autor}" if autor else "")
                + " · Misma calidad de la colección"
            )
            item["badge_marketing"] = "Próximamente"
        out.append(item)
    return out

"""Score de viabilidad — ¿necesita Presencia digital?"""

from __future__ import annotations


def score_lead(lead: dict) -> dict:
    score = 0
    senales: list[str] = []

    web = (lead.get("web") or "").strip()
    if not web:
        score += 35
        senales.append("sin_web")
    elif any(x in web.lower() for x in ("facebook.com", "instagram.com", "linktr.ee", "wa.me")):
        score += 20
        senales.append("solo_red_social")

    resenas = int(lead.get("resenas") or 0)
    if resenas < 10:
        score += 25
        senales.append("pocas_resenas")
    elif resenas < 30:
        score += 10
        senales.append("resenas_medias")

    rating = float(lead.get("rating") or 0)
    if 0 < rating < 4.0:
        score += 15
        senales.append("rating_bajo")

    if lead.get("telefono"):
        score += 5
        senales.append("tiene_telefono")
    else:
        senales.append("sin_telefono")

    score = min(score, 100)
    viable = score >= 50

    return {
        **lead,
        "score": score,
        "senales": senales,
        "viable": viable,
    }

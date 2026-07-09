"""Búsqueda Google Places API (Text Search + Details)."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
import json


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_places(query: str, api_key: str, limit: int = 10) -> list[dict]:
    q = urllib.parse.quote(query)
    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={q}&key={api_key}&language=es"
    )
    data = _get(url)
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        raise RuntimeError(f"Places API: {data.get('status')} — {data.get('error_message', '')}")

    results = data.get("results", [])[:limit]
    leads: list[dict] = []
    for r in results:
        pid = r.get("place_id", "")
        detail = _place_details(pid, api_key) if pid else {}
        leads.append(
            {
                "nombre": r.get("name", ""),
                "direccion": r.get("formatted_address", ""),
                "telefono": detail.get("formatted_phone_number", ""),
                "web": detail.get("website", ""),
                "rating": r.get("rating"),
                "resenas": r.get("user_ratings_total", 0),
                "maps_url": detail.get("url") or f"https://www.google.com/maps/place/?q=place_id:{pid}",
                "place_id": pid,
            }
        )
    return leads


def _place_details(place_id: str, api_key: str) -> dict:
    fields = "formatted_phone_number,website,url"
    pid = urllib.parse.quote(place_id)
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={pid}&fields={fields}&key={api_key}&language=es"
    )
    try:
        data = _get(url)
        return data.get("result", {}) if data.get("status") == "OK" else {}
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}

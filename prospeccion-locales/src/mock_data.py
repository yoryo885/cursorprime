"""Leads demo — modo mock sin API."""

from __future__ import annotations


def mock_leads(rubro: str, ciudad: str, limit: int = 10) -> list[dict]:
    base = [
        {
            "nombre": f"{rubro.title()} Central {ciudad}",
            "direccion": f"Av. Principal 100, {ciudad}",
            "telefono": "+56912345678",
            "web": "",
            "rating": 3.8,
            "resenas": 6,
            "maps_url": "https://maps.google.com/?q=mock1",
            "place_id": "mock-1",
        },
        {
            "nombre": f"Clínica {rubro.title()} Norte",
            "direccion": f"Los Leones 450, {ciudad}",
            "telefono": "+56987654321",
            "web": "https://facebook.com/clinica.demo",
            "rating": 4.2,
            "resenas": 18,
            "maps_url": "https://maps.google.com/?q=mock2",
            "place_id": "mock-2",
        },
        {
            "nombre": f"Servicios {rubro.title()} Express",
            "direccion": f"Mapocho 2200, {ciudad}",
            "telefono": "+56222334455",
            "web": "https://ejemplo-dental-antiguo.cl",
            "rating": 4.5,
            "resenas": 42,
            "maps_url": "https://maps.google.com/?q=mock3",
            "place_id": "mock-3",
        },
        {
            "nombre": f"{rubro.title()} Familiar",
            "direccion": f"Providencia 800, {ciudad}",
            "telefono": "",
            "web": "",
            "rating": 3.2,
            "resenas": 3,
            "maps_url": "https://maps.google.com/?q=mock4",
            "place_id": "mock-4",
        },
        {
            "nombre": f"Centro {rubro.title()} Premium",
            "direccion": f"Apoquindo 3000, {ciudad}",
            "telefono": "+56911112222",
            "web": "https://centro-premium.cl",
            "rating": 4.8,
            "resenas": 120,
            "maps_url": "https://maps.google.com/?q=mock5",
            "place_id": "mock-5",
        },
    ]
    return base[:limit]

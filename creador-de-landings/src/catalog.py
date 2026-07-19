"""Catálogo libro × rol."""

from __future__ import annotations

from pathlib import Path

from src.config import META_DIR, load_json, save_json, slug_inputs


def default_catalog_path() -> Path:
    return META_DIR / "catalogo_default.json"


def load_catalog(slug: str | None = None) -> dict:
    if slug:
        custom = slug_inputs(slug) / "catalogo.json"
        if custom.exists():
            return load_json(custom, {}) or {}
    return load_json(default_catalog_path(), {}) or {}


def ensure_catalog(slug: str, catalog: dict | None = None) -> dict:
    data = catalog or load_catalog(slug)
    dest = slug_inputs(slug) / "catalogo.json"
    if not dest.exists():
        save_json(dest, data)
    return load_json(dest, data) or data


def roles_from_catalog(catalog: dict) -> list[dict]:
    return list(catalog.get("roles") or [])


def guias_from_catalog(catalog: dict) -> list[dict]:
    return list(catalog.get("catalogo_guias") or [])


def serie_from_catalog(catalog: dict) -> list[dict]:
    return list(catalog.get("serie_libros") or [])

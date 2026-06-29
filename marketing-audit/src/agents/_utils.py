"""Utilidades para agentes de dimensión."""

from __future__ import annotations

from typing import Any


def clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def severity_from_score(score: int) -> str:
    if score < 40:
        return "critical"
    if score < 55:
        return "high"
    if score < 70:
        return "medium"
    return "low"

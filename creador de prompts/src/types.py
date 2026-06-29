"""Tipos compartidos."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentResult:
    ok: bool
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class PipelineContext:
    slug: str
    paths: dict[str, Path]
    solicitud: dict
    constitution: dict
    proyecto: dict | None = None

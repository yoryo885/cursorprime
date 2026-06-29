"""Tipos compartidos."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineContext:
    slug: str
    paths: dict[str, Path]
    lote: dict[str, Any]
    constitution: dict[str, Any]
    salidas: list[str] = field(default_factory=lambda: ["png"])
    mock_generate: bool = True


@dataclass
class AgentResult:
    ok: bool
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)

"""Tipos — Project Lens."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class PipelineContext:
    slug: str
    paths: dict[str, Path]
    idea: dict[str, Any]
    constitution: dict[str, Any]
    weights: dict[str, Any]
    modo: str = "full"
    mock_web: bool = True

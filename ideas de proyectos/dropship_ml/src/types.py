"""Tipos compartidos del pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineContext:
    slug: str
    paths: dict[str, Path]
    config: dict[str, Any]
    constitution: dict[str, Any]
    mock_scraper: bool = True
    mock_ml_api: bool = True


@dataclass
class AgentResult:
    ok: bool
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

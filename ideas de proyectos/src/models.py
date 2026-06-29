"""Modelos del meta-creador."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentResult:
    ok: bool
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class PipelineContext:
    slug: str
    borrador_dir: Path
    proyecto_dir: Path
    idea: dict[str, Any]
    autorizado_construir: bool = False

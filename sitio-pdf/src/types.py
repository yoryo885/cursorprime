from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentResult:
    ok: bool
    notes: str = ""
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineContext:
    slug: str
    producto: str
    mock: bool = True
    paths: dict[str, Path] = field(default_factory=dict)
    marca: dict[str, Any] = field(default_factory=dict)
    kdp: dict[str, Any] = field(default_factory=dict)
    assets: dict[str, str] = field(default_factory=dict)
    copy: dict[str, Any] = field(default_factory=dict)

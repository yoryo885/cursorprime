"""Checkpoint para reanudar pipeline desde un paso intermedio."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import CHECKPOINT_ENABLED, save_json, slug_meta, load_json


@dataclass
class Checkpoint:
    slug: str
    last_completed_step: int = 0
    last_completed_slug: str = ""
    updated_at: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return slug_meta(self.slug) / ".checkpoint.json"

    @classmethod
    def load(cls, slug: str) -> "Checkpoint":
        path = slug_meta(slug) / ".checkpoint.json"
        if not path.exists():
            return cls(slug=slug)
        data = load_json(path)
        return cls(
            slug=slug,
            last_completed_step=data.get("last_completed_step", 0),
            last_completed_slug=data.get("last_completed_slug", ""),
            updated_at=data.get("updated_at", ""),
            history=data.get("history", []),
        )

    def save(self) -> None:
        if not CHECKPOINT_ENABLED:
            return
        self.updated_at = datetime.now(timezone.utc).isoformat()
        save_json(
            self.path,
            {
                "slug": self.slug,
                "last_completed_step": self.last_completed_step,
                "last_completed_slug": self.last_completed_slug,
                "updated_at": self.updated_at,
                "history": self.history,
            },
        )

    def mark_completed(self, step_id: int, step_slug: str, notes: str = "") -> None:
        self.last_completed_step = step_id
        self.last_completed_slug = step_slug
        self.history.append(
            {
                "step_id": step_id,
                "step_slug": step_slug,
                "notes": notes,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.save()

    def reset(self) -> None:
        self.last_completed_step = 0
        self.last_completed_slug = ""
        self.history = []
        if self.path.exists():
            self.path.unlink()

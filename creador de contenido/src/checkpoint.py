"""Checkpoint — escribe y reanuda desde el último paso completado."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import CHECKPOINT_ENABLED, load_json, save_json, slug_meta


@dataclass
class Checkpoint:
    slug: str
    last_completed_step: int = 0
    last_completed_slug: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return slug_meta(self.slug) / ".checkpoint.json"

    @classmethod
    def load(cls, slug: str) -> "Checkpoint":
        p = slug_meta(slug) / ".checkpoint.json"
        if not p.exists():
            return cls(slug=slug)
        d = load_json(p, {}) or {}
        last_slug = d.get("last_completed_slug") or ""
        if not last_slug and d.get("history"):
            last_slug = str((d["history"][-1] or {}).get("step_slug") or "")
        return cls(
            slug=slug,
            last_completed_step=int(d.get("last_completed_step") or 0),
            last_completed_slug=last_slug,
            history=list(d.get("history") or []),
        )

    def save(self) -> None:
        if not CHECKPOINT_ENABLED:
            return
        save_json(
            self.path,
            {
                "slug": self.slug,
                "last_completed_step": self.last_completed_step,
                "last_completed_slug": self.last_completed_slug,
                "history": self.history,
                "updated_at": datetime.now(timezone.utc).isoformat(),
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

    def completed_slugs(self) -> set[str]:
        return {str(h.get("step_slug")) for h in self.history if h.get("step_slug")}

    def reset(self) -> None:
        self.last_completed_step = 0
        self.last_completed_slug = ""
        self.history = []
        if self.path.exists():
            self.path.unlink()

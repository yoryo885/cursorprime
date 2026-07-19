"""Checkpoint por slug."""

from __future__ import annotations

import json

from src.config import CHECKPOINT_ENABLED, slug_meta


class Checkpoint:
    def __init__(self, slug: str):
        self.path = slug_meta(slug) / "checkpoint.json"
        self.slug = slug

    @classmethod
    def load(cls, slug: str) -> "Checkpoint":
        return cls(slug)

    def _read(self) -> dict:
        if not self.path.exists():
            return {"completed": []}
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    def is_done(self, step: str) -> bool:
        if not CHECKPOINT_ENABLED:
            return False
        return step in self._read().get("completed", [])

    def mark(self, step: str) -> None:
        data = self._read()
        done = data.setdefault("completed", [])
        if step not in done:
            done.append(step)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def reset(self) -> None:
        if self.path.exists():
            self.path.unlink()

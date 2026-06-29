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

    def reset(self) -> None:
        if self.path.exists():
            self.path.unlink()

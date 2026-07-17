from __future__ import annotations

import json
from pathlib import Path

from src.config import ROOT, load_json, save_json


class Checkpoint:
    def __init__(self, slug: str):
        self.path = ROOT / "data" / slug / "meta" / "checkpoint.json"
        self.data = load_json(self.path, {"completed": []}) or {"completed": []}

    def is_done(self, step: str) -> bool:
        return step in self.data.get("completed", [])

    def mark(self, step: str) -> None:
        done = self.data.setdefault("completed", [])
        if step not in done:
            done.append(step)
        save_json(self.path, self.data)

    def reset(self) -> None:
        save_json(self.path, {"completed": []})

    @classmethod
    def load(cls, slug: str) -> Checkpoint:
        return cls(slug)

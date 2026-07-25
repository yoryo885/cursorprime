"""Cliente LLM local al proyecto — mock por defecto; Claude si hay API key."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from src.config import env_bool

MOCK_LLM = env_bool("MOCK_LLM", True)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise
        return json.loads(m.group(0))


class LLMClient:
    def __init__(self, mock: bool | None = None):
        self.mock = MOCK_LLM if mock is None else mock
        if not self.mock and not ANTHROPIC_API_KEY:
            self.mock = True
        self._client = None
        if not self.mock:
            from anthropic import Anthropic

            self._client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def complete_json(self, system: str, user: str, *, mock_payload: dict | None = None) -> dict:
        if self.mock:
            return dict(mock_payload or {})
        msg = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=system + "\n\nResponde SOLO con JSON válido, sin markdown.",
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return _extract_json(text)


_CLIENT: LLMClient | None = None


def get_llm() -> LLMClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = LLMClient()
    return _CLIENT


def llm_activo() -> bool:
    return not get_llm().mock

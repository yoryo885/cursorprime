"""Cliente LLM — Claude API + mock determinista para MVP sin clave."""

from __future__ import annotations

import json
import re
from typing import Any

from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MOCK_LLM


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group(0))
        raise


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

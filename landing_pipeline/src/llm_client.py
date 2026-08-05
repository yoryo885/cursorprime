"""Cliente LLM (Claude) + modo mock sin API."""

from __future__ import annotations

import json
import os
import re
from typing import Any


class LLMClient:
    """Usa Anthropic si hay ANTHROPIC_API_KEY; si no, mock determinista."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
        mock_flag = os.getenv("LANDING_MOCK", "").strip()
        self.mock = mock_flag == "1" or not self.api_key
        self._client = None
        if not self.mock:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=self.api_key)
            except Exception:
                self.mock = True

    def complete_json(self, system: str, user: str, mock_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Devuelve un dict JSON. En mock usa mock_payload (obligatorio si mock)."""
        if self.mock:
            if mock_payload is None:
                raise ValueError("Modo mock requiere mock_payload")
            return dict(mock_payload)

        text = self._call(system, user)
        return self._parse_json(text)

    def complete_text(self, system: str, user: str, mock_text: str = "") -> str:
        if self.mock:
            return mock_text
        return self._call(system, user)

    def _call(self, system: str, user: str) -> str:
        assert self._client is not None
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parts = []
        for block in msg.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence:
            text = fence.group(1).strip()
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"LLM no devolvió JSON válido: {text[:200]}")

from __future__ import annotations

from typing import Any, Protocol


class LLMClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float,
        json_mode: bool,
    ) -> str | dict:
        ...

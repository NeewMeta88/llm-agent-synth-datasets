from __future__ import annotations

import json
import os
from typing import Any

from dataset_generator.llm.base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str | dict:
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - depends on optional dep
            raise RuntimeError(
                "openai package is missing; reinstall dependencies (pip install -e .)"
            ) from exc

        try:
            client = OpenAI(base_url=self.base_url, api_key="ollama")
            response = client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else None,
            )
        except Exception as exc:
            raise RuntimeError(f"Ollama server unavailable at {self.base_url}") from exc

        content = response.choices[0].message.content
        if json_mode:
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except json.JSONDecodeError as exc:
                    raise ValueError("Invalid JSON response from Ollama") from exc
            if isinstance(content, dict):
                return content
        return content

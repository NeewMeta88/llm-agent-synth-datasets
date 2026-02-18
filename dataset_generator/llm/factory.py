from __future__ import annotations

import os

from dataset_generator.llm.base import LLMClient


class NoneLLMClient(LLMClient):
    def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        json_mode: bool,
    ) -> str | dict:
        raise RuntimeError("LLM provider is none")


def get_llm_client(
    provider: str,
    *,
    model: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.2,
) -> LLMClient:
    if provider == "none":
        return NoneLLMClient()
    if provider == "ollama":
        from dataset_generator.llm.ollama_client import OllamaClient

        model_final = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url_final = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434/v1/"
        )
        return OllamaClient(base_url=base_url_final, model=model_final)
    raise ValueError("Unsupported LLM provider")

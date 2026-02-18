import types

import pytest

from dataset_generator.llm.factory import get_llm_client
from dataset_generator.llm.ollama_client import OllamaClient


class _FakeCompletions:
    @staticmethod
    def create(*args, **kwargs):
        raise Exception("down")


class _FakeChat:
    completions = _FakeCompletions()


class _FakeOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = _FakeChat()


def test_ollama_unavailable_error(monkeypatch):
    fake_openai = types.SimpleNamespace(OpenAI=_FakeOpenAI)
    monkeypatch.setitem(__import__("sys").modules, "openai", fake_openai)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/")

    client = OllamaClient()
    with pytest.raises(RuntimeError) as exc:
        client.chat(messages=[], model="llama3.2", temperature=0.2, json_mode=False)
    assert "Ollama server unavailable" in str(exc.value)


def test_provider_none_no_ollama_required():
    client = get_llm_client("none")
    assert client is not None

from dataset_generator.llm import factory
import dataset_generator.llm.ollama_client as ollama_client


def test_ollama_cli_model_over_env(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")

    captured = {}

    class DummyClient:
        def __init__(self, base_url=None, model=None) -> None:
            captured["model"] = model
            captured["base_url"] = base_url

    monkeypatch.setattr(ollama_client, "OllamaClient", DummyClient)

    client = factory.get_llm_client(
        "ollama", model="qwen3:8b", base_url=None, temperature=0.2
    )
    assert isinstance(client, DummyClient)
    assert captured["model"] == "qwen3:8b"

from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline


class DummyLLMClient:
    model = "dummy"
    base_url = "http://dummy"

    def chat(self, messages, model, temperature, json_mode):
        return {
            "use_cases": [
                {
                    "name": "LLM UC 1",
                    "description": "LLM desc 1",
                    "anchor_phrases": ["FAQ"],
                },
                {
                    "name": "LLM UC 2",
                    "description": "LLM desc 2",
                    "anchor_phrases": ["FAQ"],
                },
            ],
            "policies": [
                {
                    "statement": "LLM Policy 1",
                    "type": "must",
                    "anchor_phrases": ["FAQ"],
                }
            ],
        }


def test_llm_drafts_used_for_ollama(tmp_path: Path, monkeypatch) -> None:
    from dataset_generator import pipeline as pipeline_module

    monkeypatch.setattr(
        pipeline_module, "get_llm_client", lambda *args, **kwargs: DummyLLMClient()
    )

    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support_llm"
    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=5,
        case="auto",
        n_use_cases=5,
        n_test_cases_per_uc=3,
        n_examples_per_tc=1,
        llm_provider="ollama",
        llm_model=None,
        ollama_base_url=None,
        llm_temperature=0.2,
    )
    run_pipeline(config)

    use_cases_text = (out_dir / "use_cases.json").read_text(encoding="utf-8")
    assert "LLM UC" in use_cases_text

    out_dir_none = tmp_path / "out" / "support_none"
    config_none = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir_none),
        seed=5,
        case="auto",
        n_use_cases=5,
        n_test_cases_per_uc=3,
        n_examples_per_tc=1,
        llm_provider="none",
        llm_model=None,
        ollama_base_url=None,
        llm_temperature=0.2,
    )
    run_pipeline(config_none)

    use_cases_text_none = (out_dir_none / "use_cases.json").read_text(encoding="utf-8")
    assert "LLM UC" not in use_cases_text_none

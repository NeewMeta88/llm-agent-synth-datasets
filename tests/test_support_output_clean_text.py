import json
from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline


def test_support_output_clean_text(tmp_path: Path) -> None:
    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support"

    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=3,
        case="auto",
        n_use_cases=5,
        n_test_cases_per_uc=3,
        n_examples_per_tc=1,
        llm_provider="none",
        llm_model=None,
        ollama_base_url=None,
        llm_temperature=0.2,
    )
    run_pipeline(config)

    dataset_path = out_dir / "dataset.json"
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    examples = data["examples"]

    bad_tokens = ["**", "\\+", "|", "##"]
    unique_users = set()
    unique_expected = set()
    for ex in examples:
        if ex.get("case") != "support_bot":
            continue
        metadata = ex.get("metadata", {})
        source = metadata.get("source")
        if source not in {"tickets", "faq_paraphrase"}:
            continue
        messages = ex.get("input", {}).get("messages", [])
        if messages:
            content = messages[0].get("content", "")
            for token in bad_tokens:
                assert token not in content
            unique_users.add(content)
        expected = ex.get("expected_output", "")
        for token in bad_tokens:
            assert token not in expected
        unique_expected.add(expected)

    assert len(unique_users) >= 5
    assert len(unique_expected) >= 5

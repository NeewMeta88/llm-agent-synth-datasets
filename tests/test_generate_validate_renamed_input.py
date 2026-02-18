from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline
from dataset_generator.validate.validator import validate_out_dir


def test_generate_validate_with_renamed_input(tmp_path: Path) -> None:
    source_input = Path("examples") / "example_input_raw_support.md"
    renamed_input = tmp_path / "renamed_support_input.md"
    renamed_input.write_text(source_input.read_text(encoding="utf-8"), encoding="utf-8")

    out_dir = tmp_path / "out" / "support"
    config = PipelineConfig(
        input_path=str(renamed_input),
        out_dir=str(out_dir),
        seed=7,
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

    ok, errors, _ = validate_out_dir(out_dir)
    assert ok, errors

    use_cases = (out_dir / "use_cases.json").read_text(encoding="utf-8")
    policies = (out_dir / "policies.json").read_text(encoding="utf-8")
    assert renamed_input.name in use_cases
    assert renamed_input.name in policies

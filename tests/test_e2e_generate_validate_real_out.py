from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline
from dataset_generator.validate.validator import validate_out_dir


def test_e2e_generate_validate_real_out_support(tmp_path: Path) -> None:
    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support"

    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=11,
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


def test_e2e_generate_validate_real_out_operator_quality(tmp_path: Path) -> None:
    input_path = Path("examples") / "example_input_raw_operator_quality_checks.md"
    out_dir = tmp_path / "out" / "operator_quality"

    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=12,
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

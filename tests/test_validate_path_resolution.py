import os
from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline
from dataset_generator.validate.validator import validate_out_dir


def test_validate_path_resolution(tmp_path: Path) -> None:
    input_path = "examples/example_input_raw_support.md"
    out_dir = tmp_path / "out" / "support"

    config = PipelineConfig(
        input_path=input_path,
        out_dir=str(out_dir),
        seed=1,
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

    cwd_before = Path.cwd()
    os.chdir(out_dir)
    try:
        ok, errors, _ = validate_out_dir(out_dir)
    finally:
        os.chdir(cwd_before)

    assert ok, errors

from pathlib import Path
from typing import Literal

import typer

from dataset_generator.pipeline import PipelineConfig, run_pipeline
from dataset_generator.validate.validator import format_report, validate_out_dir

app = typer.Typer(add_completion=False)


@app.command()
def generate(
    input_path: Path = typer.Option(..., "--input", help="Path to input data."),
    out_dir: Path = typer.Option(..., "--out", help="Output directory."),
    seed: int = typer.Option(..., "--seed", help="Random seed."),
    case: Literal["support_bot", "operator_quality", "auto"] = typer.Option(
        "auto",
        "--case",
        help="Generation case.",
        show_default=True,
    ),
    n_use_cases: int = typer.Option(
        5,
        "--n-use-cases",
        help="Number of use cases.",
        show_default=True,
    ),
    n_test_cases_per_uc: int = typer.Option(
        3,
        "--n-test-cases-per-uc",
        help="Number of test cases per use case.",
        show_default=True,
    ),
    n_examples_per_tc: int = typer.Option(
        1,
        "--n-examples-per-tc",
        help="Number of examples per test case.",
        show_default=True,
    ),
    llm_provider: Literal["none", "ollama", "openai"] = typer.Option(
        "none",
        "--llm-provider",
        help="LLM provider.",
        show_default=True,
    ),
    llm_model: str | None = typer.Option(
        None,
        "--llm-model",
        help="LLM model (CLI overrides env).",
        show_default=False,
    ),
    ollama_base_url: str | None = typer.Option(
        None,
        "--ollama-base-url",
        help="Ollama base URL (CLI overrides env).",
        show_default=False,
    ),
    llm_temperature: float = typer.Option(
        0.2,
        "--temperature",
        "--llm-temperature",
        help="LLM temperature.",
        show_default=True,
    ),
) -> None:
    """Generate datasets (stub)."""
    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=seed,
        case=case,
        n_use_cases=n_use_cases,
        n_test_cases_per_uc=n_test_cases_per_uc,
        n_examples_per_tc=n_examples_per_tc,
        llm_provider=llm_provider,
        llm_model=llm_model,
        ollama_base_url=ollama_base_url,
        llm_temperature=llm_temperature,
    )
    run_pipeline(config)
    typer.echo(f"Generated dataset at {out_dir}")


@app.command()
def validate(
    out_dir: Path = typer.Option(..., "--out", help="Output directory to validate."),
) -> None:
    """Validate generated datasets (stub)."""
    ok, errors, counts = validate_out_dir(out_dir)
    if any("Schema error" in err and "required property" in err for err in errors):
        typer.echo(
            "WARNING: Возможно, out_dir сгенерен старой версией. Пересоздайте через generate."
        )
    typer.echo(format_report(ok, errors, counts))
    if not ok:
        raise typer.Exit(code=1)

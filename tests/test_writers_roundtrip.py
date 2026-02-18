import json
from pathlib import Path

from dataset_generator.core.models import RunManifest, UseCase, Evidence
from dataset_generator.io.writers import write_run_manifest, write_use_cases


def test_writers_roundtrip(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"

    manifest = RunManifest(
        seed=123,
        timestamp="2026-02-17T00:00:00Z",
        generator_version="0.1.0",
        llm={},
        input_path="input.md",
        out_path=str(out_dir),
    )
    manifest_path = write_run_manifest(out_dir, manifest)

    use_cases = [
        UseCase(
            id="uc_1",
            case="support_bot",
            name="Example",
            description="Desc",
            evidence=[
                Evidence(
                    input_file="input.md",
                    line_start=1,
                    line_end=1,
                    quote="Line",
                )
            ],
        )
    ]
    use_cases_path = write_use_cases(out_dir, use_cases)

    assert manifest_path.exists()
    assert use_cases_path.exists()

    with manifest_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["seed"] == 123

    with use_cases_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["use_cases"][0]["id"] == "uc_1"

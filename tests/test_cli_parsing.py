import json
import subprocess
import sys
from pathlib import Path


def test_cli_generate_without_subcommand(tmp_path: Path) -> None:
    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataset_generator",
            "--input",
            str(input_path),
            "--out",
            str(out_dir),
            "--seed",
            "1",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["input_path"] == str(input_path)


def test_cli_validate_subcommand(tmp_path: Path) -> None:
    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "dataset_generator",
            "--input",
            str(input_path),
            "--out",
            str(out_dir),
            "--seed",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "-m", "dataset_generator", "validate", "--out", str(out_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

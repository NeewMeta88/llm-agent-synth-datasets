import subprocess
import sys


def test_cli_help_exit_code_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dataset_generator", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_generate_help_exit_code_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dataset_generator", "generate", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_validate_help_exit_code_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dataset_generator", "validate", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_generate_requires_args() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dataset_generator", "generate"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Missing option" in (result.stderr + result.stdout)

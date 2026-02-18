from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    current = start
    for _ in range(6):
        if (current / "pyproject.toml").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start


def _find_validator(repo_root: Path) -> Path | None:
    candidates = [
        repo_root / "official_validator.py",
        repo_root.parent / "official_validator.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _run_validator(validator: Path, out_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(validator), "--out", str(out_path)],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run official_validator.py for both outputs if present."
    )
    parser.add_argument("--support-out", required=True, help="Support output directory")
    parser.add_argument(
        "--operator-out", required=True, help="Operator quality output directory"
    )
    args = parser.parse_args()

    repo_root = _find_repo_root(Path(__file__).resolve())
    validator = _find_validator(repo_root)
    if validator is None:
        print("official_validator.py not found; skipping.")
        return 0

    _run_validator(validator, Path(args.support_out))
    _run_validator(validator, Path(args.operator_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

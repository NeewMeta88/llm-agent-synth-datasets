from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataset_generator.core.models import DatasetExample, Policy, RunManifest, TestCase, UseCase


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def write_json(path: str | Path, data_dict: Any) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    with target.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_use_cases(out_dir: str | Path, items: list[UseCase]) -> Path:
    target_dir = ensure_dir(out_dir)
    target = target_dir / "use_cases.json"
    write_json(target, {"use_cases": [u.model_dump() for u in items]})
    return target


def write_policies(out_dir: str | Path, items: list[Policy]) -> Path:
    target_dir = ensure_dir(out_dir)
    target = target_dir / "policies.json"
    write_json(target, {"policies": [p.model_dump() for p in items]})
    return target


def write_test_cases(out_dir: str | Path, items: list[TestCase]) -> Path:
    target_dir = ensure_dir(out_dir)
    target = target_dir / "test_cases.json"
    write_json(target, {"test_cases": [t.model_dump() for t in items]})
    return target


def write_dataset(out_dir: str | Path, items: list[DatasetExample]) -> Path:
    target_dir = ensure_dir(out_dir)
    target = target_dir / "dataset.json"
    write_json(target, {"examples": [e.model_dump() for e in items]})
    return target


def write_run_manifest(out_dir: str | Path, item: RunManifest) -> Path:
    target_dir = ensure_dir(out_dir)
    target = target_dir / "run_manifest.json"
    write_json(target, item.model_dump())
    return target

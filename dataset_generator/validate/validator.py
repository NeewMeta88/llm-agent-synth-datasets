from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from dataset_generator.core.markdown import MarkdownDocument


REQUIRED_FILES = {
    "use_cases.json",
    "policies.json",
    "test_cases.json",
    "dataset.json",
    "run_manifest.json",
}

ALLOWED_ID_PREFIXES = {
    "use_cases.json": "uc_",
    "policies.json": "pol_",
    "test_cases.json": "tc_",
    "dataset.json": "ex_",
}

ALLOWED_ROLES = {"system", "user", "assistant", "operator"}
ALLOWED_CASES = {"support_bot", "operator_quality", "doctor_booking"}
ALLOWED_FORMATS = {
    "single_turn_qa",
    "single_utterance_correction",
    "dialog_last_turn_correction",
}
ALLOWED_POLICY_TYPES = {"must", "must_not", "escalate", "style", "format"}
ALLOWED_SPLITS = {"train", "test", "corner"}
SUPPORT_BOT_SOURCES = {"tickets", "faq_paraphrase", "corner"}
MIN_UNIQUE_USER_CONTENTS = 5
MIN_UNIQUE_EXPECTED_OUTPUTS = 5
MIN_EXAMPLES_FOR_DIVERSITY_CHECK = 15


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _schema_for_list(container_key: str, required_fields: list[str]) -> dict:
    return {
        "type": "object",
        "required": [container_key],
        "properties": {
            container_key: {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": required_fields,
                    "properties": {key: {} for key in required_fields},
                },
            }
        },
    }


def _schema_for_manifest() -> dict:
    return {
        "type": "object",
        "required": [
            "seed",
            "timestamp",
            "generator_version",
            "llm",
            "input_path",
            "out_path",
        ],
    }


def validate_out_dir(out_dir: str | Path) -> tuple[bool, list[str], dict[str, int]]:
    out_path = Path(out_dir)
    errors: list[str] = []
    counts: dict[str, int] = {}

    missing = [name for name in REQUIRED_FILES if not (out_path / name).exists()]
    if missing:
        for name in missing:
            errors.append(f"Missing file: {name}")
        return False, errors, counts

    use_cases_doc = _load_json(out_path / "use_cases.json")
    policies_doc = _load_json(out_path / "policies.json")
    test_cases_doc = _load_json(out_path / "test_cases.json")
    dataset_doc = _load_json(out_path / "dataset.json")
    manifest = _load_json(out_path / "run_manifest.json")

    use_cases = use_cases_doc.get("use_cases", []) if isinstance(use_cases_doc, dict) else []
    policies = policies_doc.get("policies", []) if isinstance(policies_doc, dict) else []
    test_cases = (
        test_cases_doc.get("test_cases", []) if isinstance(test_cases_doc, dict) else []
    )
    dataset = dataset_doc.get("examples", []) if isinstance(dataset_doc, dict) else []

    counts["use_cases"] = len(use_cases)
    counts["policies"] = len(policies)
    counts["test_cases"] = len(test_cases)
    counts["dataset"] = len(dataset)
    formats_count: dict[str, int] = {}
    for ex in dataset:
        fmt = ex.get("format") if isinstance(ex, dict) else None
        if isinstance(fmt, str):
            formats_count[fmt] = formats_count.get(fmt, 0) + 1
    counts["formats"] = formats_count

    schema_map = {
        "use_cases.json": _schema_for_list(
            "use_cases", ["id", "case", "name", "description", "evidence"]
        ),
        "policies.json": _schema_for_list(
            "policies", ["id", "case", "type", "statement", "evidence"]
        ),
        "test_cases.json": _schema_for_list(
            "test_cases",
            ["id", "case", "use_case_id", "parameters", "policy_ids", "description"],
        ),
        "dataset.json": _schema_for_list(
            "examples",
            [
                "id",
                "case",
                "format",
                "use_case_id",
                "test_case_id",
                "input",
                "expected_output",
                "evaluation_criteria",
                "policy_ids",
                "metadata",
            ]
        ),
        "run_manifest.json": _schema_for_manifest(),
    }

    data_map = {
        "use_cases.json": use_cases_doc,
        "policies.json": policies_doc,
        "test_cases.json": test_cases_doc,
        "dataset.json": dataset_doc,
        "run_manifest.json": manifest,
    }

    list_map = {
        "use_cases.json": use_cases,
        "policies.json": policies,
        "test_cases.json": test_cases,
        "dataset.json": dataset,
    }

    for name, schema in schema_map.items():
        try:
            validate(instance=data_map[name], schema=schema)
        except ValidationError as exc:
            errors.append(f"Schema error in {name}: {exc.message}")

    for file_name, prefix in ALLOWED_ID_PREFIXES.items():
        seen: set[str] = set()
        for item in list_map.get(file_name, []):
            item_id = item.get("id")
            if not isinstance(item_id, str):
                errors.append(f"{file_name}: id is missing or not a string")
                continue
            if not item_id.startswith(prefix):
                errors.append(f"{file_name}: id '{item_id}' missing prefix {prefix}")
            if item_id in seen:
                errors.append(f"{file_name}: duplicate id '{item_id}'")
            seen.add(item_id)

    markdown_cache: dict[str, MarkdownDocument] = {}

    def _resolve_input_path(path_str: str) -> Path | None:
        raw_path = Path(path_str)
        if raw_path.is_absolute():
            if raw_path.exists():
                return raw_path
            return None

        candidates = [
            (Path.cwd() / raw_path),
            (out_path / raw_path),
        ]

        repo_root = Path(__file__).resolve()
        for _ in range(5):
            if (repo_root / "pyproject.toml").exists():
                candidates.append(repo_root / raw_path)
                break
            repo_root = repo_root.parent

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    manifest_input_path = manifest.get("input_path")
    if not isinstance(manifest_input_path, str):
        errors.append("run_manifest.json: input_path missing or invalid")
        manifest_input_path = None

    def _get_md() -> MarkdownDocument | None:
        if manifest_input_path is None:
            return None
        if manifest_input_path not in markdown_cache:
            md_path = _resolve_input_path(manifest_input_path)
            if md_path is None:
                errors.append(
                    f"run_manifest.json: input_path not found: {manifest_input_path}"
                )
                return None
            markdown_cache[manifest_input_path] = MarkdownDocument.read(str(md_path))
        return markdown_cache[manifest_input_path]

    def _check_evidence(items: list[dict], context: str) -> None:
        for item in items:
            evidence_list = item.get("evidence", [])
            if not isinstance(evidence_list, list):
                errors.append(f"{context}: evidence must be list")
                continue
            for ev in evidence_list:
                input_file = ev.get("input_file")
                line_start = ev.get("line_start")
                line_end = ev.get("line_end")
                quote = ev.get("quote")
                if not isinstance(input_file, str):
                    errors.append(f"{context}: evidence.input_file missing")
                    continue
                if not isinstance(line_start, int) or not isinstance(line_end, int):
                    errors.append(f"{context}: evidence line range invalid")
                    continue
                if line_start > line_end or line_start < 1:
                    errors.append(f"{context}: evidence line range invalid")
                    continue
                md = _get_md()
                if md is None:
                    continue
                if line_end > md.n_lines:
                    errors.append(f"{context}: evidence line range out of bounds")
                    continue
                expected = md.quote(line_start, line_end)
                if quote != expected:
                    errors.append(f"{context}: evidence quote mismatch")

    _check_evidence(use_cases, "use_cases")
    _check_evidence(policies, "policies")

    for uc in use_cases:
        if uc.get("case") not in ALLOWED_CASES:
            errors.append("use_cases: case invalid")

    for pol in policies:
        if pol.get("case") not in ALLOWED_CASES:
            errors.append("policies: case invalid")
        if pol.get("type") not in ALLOWED_POLICY_TYPES:
            errors.append("policies: type invalid")

    for tc in test_cases:
        if tc.get("case") not in ALLOWED_CASES:
            errors.append("test_cases: case invalid")
        if not isinstance(tc.get("parameters"), dict):
            errors.append("test_cases: parameters must be object")

    for ex in dataset:
        evaluation = ex.get("evaluation_criteria", [])
        if not isinstance(evaluation, list) or len(evaluation) < 3:
            errors.append("dataset: evaluation_criteria must have at least 3 items")

        policy_ids = ex.get("policy_ids", [])
        if not isinstance(policy_ids, list) or len(policy_ids) < 1:
            errors.append("dataset: policy_ids must have at least 1 item")

        input_obj = ex.get("input", {})
        messages = input_obj.get("messages", []) if isinstance(input_obj, dict) else []
        if not isinstance(messages, list):
            errors.append("dataset: input.messages must be list")
        else:
            for msg in messages:
                role = msg.get("role") if isinstance(msg, dict) else None
                if role not in ALLOWED_ROLES:
                    errors.append("dataset: message role invalid")

        if ex.get("case") not in ALLOWED_CASES:
            errors.append("dataset: case invalid")
        fmt = ex.get("format")
        if fmt not in ALLOWED_FORMATS:
            errors.append("dataset: format invalid")
        if fmt == "dialog_last_turn_correction":
            tmi = input_obj.get("target_message_index") if isinstance(input_obj, dict) else None
            if not isinstance(tmi, int):
                errors.append("dataset: target_message_index required for dialog_last_turn_correction")
            else:
                if not isinstance(messages, list) or tmi < 0 or tmi >= len(messages):
                    errors.append("dataset: target_message_index out of bounds")
                else:
                    last_operator_index = None
                    for idx, msg in enumerate(messages):
                        if isinstance(msg, dict) and msg.get("role") == "operator":
                            last_operator_index = idx
                    if last_operator_index is None or tmi != last_operator_index:
                        errors.append("dataset: target_message_index must point to last operator message")

    if counts["use_cases"] < 5:
        errors.append("coverage: use_cases must be >= 5")
    if counts["policies"] < 5:
        errors.append("coverage: policies must be >= 5")

    tc_by_uc: dict[str, list[dict]] = defaultdict(list)
    for tc in test_cases:
        uc_id = tc.get("use_case_id")
        if isinstance(uc_id, str):
            tc_by_uc[uc_id].append(tc)

    for uc in use_cases:
        uc_id = uc.get("id")
        if isinstance(uc_id, str):
            if len(tc_by_uc.get(uc_id, [])) < 3:
                errors.append(f"coverage: use_case {uc_id} must have >= 3 test cases")

    ex_by_tc: dict[str, list[dict]] = defaultdict(list)
    for ex in dataset:
        tc_id = ex.get("test_case_id")
        if isinstance(tc_id, str):
            ex_by_tc[tc_id].append(ex)

    for tc in test_cases:
        tc_id = tc.get("id")
        if isinstance(tc_id, str):
            if len(ex_by_tc.get(tc_id, [])) < 1:
                errors.append(f"coverage: test_case {tc_id} must have >= 1 example")

    sources_present = set()
    support_examples = 0
    unique_user_contents: set[str] = set()
    unique_expected_outputs: set[str] = set()

    def _primary_input_text(example: dict) -> str:
        input_obj = example.get("input", {})
        messages = input_obj.get("messages", []) if isinstance(input_obj, dict) else []
        if not isinstance(messages, list):
            return ""

        if example.get("case") == "operator_quality":
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "operator":
                    content = msg.get("content")
                    return content if isinstance(content, str) else ""
        else:
            for msg in messages:
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content")
                    return content if isinstance(content, str) else ""

        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    return content
        return ""
    for ex in dataset:
        expected_output = ex.get("expected_output")
        if isinstance(expected_output, str):
            unique_expected_outputs.add(expected_output)

        primary_text = _primary_input_text(ex)
        if primary_text:
            unique_user_contents.add(primary_text)

        if ex.get("case") == "support_bot":
            support_examples += 1
            metadata = ex.get("metadata", {})
            source = metadata.get("source") if isinstance(metadata, dict) else None
            if source not in SUPPORT_BOT_SOURCES:
                errors.append("support_bot: metadata.source invalid")
            else:
                sources_present.add(source)
        metadata = ex.get("metadata", {})
        split = metadata.get("split") if isinstance(metadata, dict) else None
        if split not in ALLOWED_SPLITS:
            errors.append("dataset: metadata.split invalid")

    if support_examples > 0:
        missing_sources = SUPPORT_BOT_SOURCES - sources_present
        if missing_sources:
            errors.append(
                "support_bot: missing sources " + ", ".join(sorted(missing_sources))
            )

    if len(dataset) >= MIN_EXAMPLES_FOR_DIVERSITY_CHECK:
        if len(unique_user_contents) < MIN_UNIQUE_USER_CONTENTS:
            errors.append(
                "dataset: not enough unique primary input texts "
                f"(>= {MIN_UNIQUE_USER_CONTENTS} required)"
            )
        if len(unique_expected_outputs) < MIN_UNIQUE_EXPECTED_OUTPUTS:
            errors.append(
                "dataset: not enough unique expected_output "
                f"(>= {MIN_UNIQUE_EXPECTED_OUTPUTS} required)"
            )

    return len(errors) == 0, errors, counts


def format_report(ok: bool, errors: list[str], counts: dict[str, int]) -> str:
    lines = [
        f"use_cases: {counts.get('use_cases', 0)}",
        f"policies: {counts.get('policies', 0)}",
        f"test_cases: {counts.get('test_cases', 0)}",
        f"dataset: {counts.get('dataset', 0)}",
    ]
    formats = counts.get("formats", {})
    if isinstance(formats, dict) and formats:
        formatted = ", ".join(f"{key}={value}" for key, value in sorted(formats.items()))
        lines.append(f"formats: {formatted}")
    status = "OK" if ok else "FAILED"
    lines.insert(0, f"Validation: {status}")
    if errors:
        lines.append("Errors:")
        lines.extend([f"- {err}" for err in errors])
    return "\n".join(lines)

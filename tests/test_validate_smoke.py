import json
from pathlib import Path

from dataset_generator.validate.validator import validate_out_dir


def test_validate_smoke(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    input_md = out_dir / "input.md"
    input_md.write_text("Line1\nLine2\n", encoding="utf-8")

    use_cases = []
    for i in range(1, 6):
        use_cases.append(
            {
                "id": f"uc_{i}",
                "case": "support_bot",
                "name": f"Use Case {i}",
                "description": "Desc",
                "evidence": [
                    {
                        "input_file": "input.md",
                        "line_start": 1,
                        "line_end": 1,
                        "quote": "Line1",
                    }
                ],
            }
        )

    policies = []
    for i in range(1, 6):
        policies.append(
            {
                "id": f"pol_{i}",
                "case": "support_bot",
                "type": "must",
                "statement": f"Policy {i}",
                "evidence": [
                    {
                        "input_file": "input.md",
                        "line_start": 1,
                        "line_end": 1,
                        "quote": "Line1",
                    }
                ],
            }
        )

    test_cases = []
    tc_id = 1
    for uc_index in range(1, 6):
        for _ in range(3):
            test_cases.append(
                {
                    "id": f"tc_{tc_id}",
                    "case": "support_bot",
                    "use_case_id": f"uc_{uc_index}",
                    "parameters": {"axis": "tone"},
                    "policy_ids": ["pol_1"],
                    "description": "Test case",
                }
            )
            tc_id += 1

    dataset = []
    sources = ["tickets", "faq_paraphrase", "corner"]
    for i in range(1, 16):
        case = "support_bot" if i <= 3 else "operator_quality"
        metadata = {"source": sources[i - 1]} if i <= 3 else {}
        if case == "support_bot":
            messages = [{"role": "user", "content": f"Support message {i}"}]
            fmt = "single_turn_qa"
        else:
            messages = [
                {"role": "user", "content": f"User message {i}"},
                {"role": "operator", "content": f"Operator response {i}"},
            ]
            fmt = "single_utterance_correction"
        dataset.append(
            {
                "id": f"ex_{i}",
                "case": case,
                "format": fmt,
                "use_case_id": f"uc_{((i - 1) // 3) + 1}",
                "test_case_id": f"tc_{i}",
                "input": {
                    "messages": messages,
                    "target_message_index": None,
                },
                "expected_output": f"Expected output {i}",
                "evaluation_criteria": ["a", "b", "c"],
                "policy_ids": ["pol_1"],
                "metadata": {**metadata, "split": "train"},
            }
        )

    manifest = {
        "seed": 1,
        "timestamp": "2026-02-17T00:00:00Z",
        "generator_version": "0.1.0",
        "llm": {},
        "input_path": str(input_md),
        "out_path": str(out_dir),
    }

    (out_dir / "use_cases.json").write_text(
        json.dumps({"use_cases": use_cases}), encoding="utf-8"
    )
    (out_dir / "policies.json").write_text(
        json.dumps({"policies": policies}), encoding="utf-8"
    )
    (out_dir / "test_cases.json").write_text(
        json.dumps({"test_cases": test_cases}), encoding="utf-8"
    )
    (out_dir / "dataset.json").write_text(
        json.dumps({"examples": dataset}), encoding="utf-8"
    )
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    ok, errors, _ = validate_out_dir(out_dir)
    assert ok
    assert errors == []

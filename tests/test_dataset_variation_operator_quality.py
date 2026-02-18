from dataset_generator.core.models import Policy, TestCase, UseCase
from dataset_generator.generate.dataset import generate_examples


def test_operator_quality_variation() -> None:
    use_cases = [UseCase(id="uc_1", case="operator_quality", name="UC", description="d", evidence=[])]
    policies = [Policy(id="pol_1", case="operator_quality", type="must", statement="s", evidence=[])]
    test_cases = [
        TestCase(
            id=f"tc_{i}",
            case="operator_quality",
            use_case_id="uc_1",
            parameters={"axis": "tone"},
            policy_ids=["pol_1"],
            description=f"Test case focusing on axis: tone {i}",
        )
        for i in range(1, 16)
    ]

    examples = generate_examples(
        "operator_quality",
        test_cases,
        use_cases,
        policies,
        n_per_tc=1,
        seed=2,
    )

    unique_inputs = {ex.input.messages[-1].content for ex in examples}
    unique_expected = {ex.expected_output for ex in examples}

    assert len(unique_inputs) >= 5
    assert len(unique_expected) >= 5

    for ex in examples:
        if ex.format == "dialog_last_turn_correction":
            assert ex.input.target_message_index == len(ex.input.messages) - 1
            assert ex.input.messages[-1].role == "operator"

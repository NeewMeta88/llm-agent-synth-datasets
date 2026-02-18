from dataset_generator.core.models import Policy, TestCase, UseCase
from dataset_generator.generate.dataset import generate_examples


def test_operator_quality_invariants() -> None:
    use_cases = [UseCase(id="uc_1", case="operator_quality", name="UC", description="d", evidence=[])]
    policies = [Policy(id="pol_1", case="operator_quality", type="must", statement="s", evidence=[])]
    test_cases = [
        TestCase(
            id="tc_1",
            case="operator_quality",
            use_case_id="uc_1",
            parameters={"axis": "tone"},
            policy_ids=["pol_1"],
            description="Test case focusing on axis: tone",
        )
    ]

    examples = generate_examples(
        "operator_quality",
        test_cases,
        use_cases,
        policies,
        n_per_tc=2,
        seed=1,
    )

    for ex in examples:
        if ex.format == "dialog_last_turn_correction":
            messages = ex.input.messages
            assert ex.input.target_message_index == len(messages) - 1
            assert messages[-1].role == "operator"


def test_support_bot_sources_present() -> None:
    use_cases = [UseCase(id="uc_1", case="support_bot", name="UC", description="d", evidence=[])]
    policies = [Policy(id="pol_1", case="support_bot", type="must", statement="s", evidence=[])]
    test_cases = [
        TestCase(
            id=f"tc_{i}",
            case="support_bot",
            use_case_id="uc_1",
            parameters={"axis": "tone"},
            policy_ids=["pol_1"],
            description="Test case focusing on axis: tone",
        )
        for i in range(1, 4)
    ]

    examples = generate_examples(
        "support_bot",
        test_cases,
        use_cases,
        policies,
        n_per_tc=1,
        seed=1,
    )

    sources = {ex.metadata.get("source") for ex in examples}
    assert {"tickets", "faq_paraphrase", "corner"}.issubset(sources)

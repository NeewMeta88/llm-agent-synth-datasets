from dataset_generator.core.models import Policy, UseCase
from dataset_generator.generate.test_cases import generate_test_cases


def test_generate_test_cases_counts() -> None:
    use_cases = [
        UseCase(id=f"uc_{i}", case="support_bot", name=f"UC {i}", description="d", evidence=[])
        for i in range(1, 6)
    ]
    policies = [
        Policy(id=f"pol_{i}", case="support_bot", type="must", statement="s", evidence=[])
        for i in range(1, 6)
    ]

    test_cases = generate_test_cases(use_cases, policies, n_per_uc=3, seed=1)

    assert len(test_cases) == 15
    for tc in test_cases:
        assert tc.policy_ids

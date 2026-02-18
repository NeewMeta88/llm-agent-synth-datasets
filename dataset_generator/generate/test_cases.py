from __future__ import annotations

import random
from itertools import cycle

from dataset_generator.core.ids import IdFactory
from dataset_generator.core.models import Policy, TestCase, UseCase

_AXES = ["tone", "complexity", "edge_case", "coverage", "clarity"]


def generate_test_cases(
    use_cases: list[UseCase],
    policies: list[Policy],
    n_per_uc: int,
    seed: int,
) -> list[TestCase]:
    if n_per_uc < 1:
        return []

    rng = random.Random(seed)
    policy_cycle = cycle(policies) if policies else None
    factory = IdFactory("tc_")
    test_cases: list[TestCase] = []

    for uc in use_cases:
        for _ in range(n_per_uc):
            axis = rng.choice(_AXES)
            policy_ids: list[str]
            if policy_cycle is None:
                policy_ids = []
            else:
                policy = next(policy_cycle)
                policy_ids = [policy.id]
            description = f"Test case focusing on axis: {axis}"
            test_cases.append(
                TestCase(
                    id=factory.new(f"{uc.id}-{axis}"),
                    case="",
                    use_case_id=uc.id,
                    parameters={"axis": axis},
                    policy_ids=policy_ids,
                    description=description,
                )
            )

    return test_cases

from dataset_generator.core.models import DatasetExample, DatasetInput, Message, model_json_schema


def test_minimal_example_valid() -> None:
    example = DatasetExample(
        id="ex_1",
        case="support_bot",
        format="single_turn_qa",
        use_case_id="uc_1",
        test_case_id="tc_1",
        input=DatasetInput(
            messages=[
                Message(role="user", content="Hi"),
                Message(role="assistant", content="Hello"),
            ],
            target_message_index=1,
        ),
        expected_output="Hello",
        evaluation_criteria=["politeness"],
        policy_ids=["pol_1"],
        metadata={"split": "train"},
    )
    assert example.id == "ex_1"


def test_model_json_schema_returns_dict() -> None:
    schema = model_json_schema()
    assert isinstance(schema, dict)


def test_message_operator_role_valid() -> None:
    msg = Message(role="operator", content="OK")
    assert msg.role == "operator"

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Evidence(BaseModel):
    input_file: str
    line_start: int
    line_end: int
    quote: str


class UseCase(BaseModel):
    id: str
    case: str
    name: str
    description: str
    evidence: list[Evidence]


class Policy(BaseModel):
    id: str
    case: str
    type: str
    statement: str
    evidence: list[Evidence]


class TestCase(BaseModel):
    __test__ = False
    id: str
    case: str
    use_case_id: str
    parameters: dict
    policy_ids: list[str]
    description: str


_ALLOWED_ROLES = {"system", "user", "assistant", "operator", "tool", "developer"}


class Message(BaseModel):
    role: str
    content: Any

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in _ALLOWED_ROLES:
            raise ValueError("Unsupported role")
        return value


class DatasetInput(BaseModel):
    messages: list[Message]
    target_message_index: int | None = None


class DatasetExample(BaseModel):
    id: str
    case: str
    format: str
    use_case_id: str
    test_case_id: str
    input: DatasetInput
    expected_output: str
    evaluation_criteria: list[str]
    policy_ids: list[str]
    metadata: dict


class RunManifest(BaseModel):
    seed: int
    timestamp: str
    generator_version: str
    llm: dict
    input_path: str
    out_path: str


def to_json(obj: Any) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    raise TypeError("Object does not support model_dump")


def model_json_schema() -> dict:
    return {
        "Evidence": Evidence.model_json_schema(),
        "UseCase": UseCase.model_json_schema(),
        "Policy": Policy.model_json_schema(),
        "TestCase": TestCase.model_json_schema(),
        "Message": Message.model_json_schema(),
        "DatasetInput": DatasetInput.model_json_schema(),
        "DatasetExample": DatasetExample.model_json_schema(),
        "RunManifest": RunManifest.model_json_schema(),
    }

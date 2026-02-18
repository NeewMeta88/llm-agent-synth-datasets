from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dataset_generator.core.ids import IdFactory
from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.core.models import Evidence, Policy, UseCase
from dataset_generator.core.text_sanitize import sanitize_markdown_text


@dataclass(frozen=True)
class UseCaseDraft:
    name: str
    description: str
    anchor_phrases: list[str]


@dataclass(frozen=True)
class PolicyDraft:
    statement: str
    type: str
    anchor_phrases: list[str]


def _normalize_anchors(text: str, anchors: list[str] | None) -> list[str]:
    if anchors:
        cleaned = [a.strip() for a in anchors if a.strip()]
    else:
        cleaned = []
    if not cleaned:
        cleaned = [text.strip()]
    return cleaned[:3]


def _normalize_policy_type(value: str | None) -> str:
    if not value:
        return "must"
    lowered = value.lower()
    if lowered in {"must", "must_not", "escalate", "style", "format"}:
        return lowered
    return "must"


def extract_drafts(
    doc: MarkdownDocument,
    llm_client,
    case: str,
    seed: int,
    temperature: float = 0.2,
) -> tuple[list[UseCaseDraft], list[PolicyDraft]]:
    system = (
        "You extract structured drafts of use cases and policies from markdown."
        " Return JSON with keys use_cases and policies."
        " use_cases: [{name, description, anchor_phrases}]"
        " policies: [{statement, type, anchor_phrases}]"
    )
    user = (
        f"Case: {case}. Seed: {seed}. Extract drafts from the document below.\n\n"
        + "\n".join(doc.lines[:2000])
    )
    response = llm_client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=getattr(llm_client, "model", None) or "default",
        temperature=temperature,
        json_mode=True,
    )
    if isinstance(response, str):
        try:
            import json

            payload = json.loads(response)
        except Exception:
            payload = {}
    elif isinstance(response, dict):
        payload = response
    else:
        payload = {}

    use_cases_raw = payload.get("use_cases", []) if isinstance(payload, dict) else []
    policies_raw = payload.get("policies", []) if isinstance(payload, dict) else []

    use_cases: list[UseCaseDraft] = []
    for item in use_cases_raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        description = str(item.get("description", "")).strip()
        anchors = _normalize_anchors(name or description, item.get("anchor_phrases"))
        if name or description:
            use_cases.append(
                UseCaseDraft(
                    name=name or "Use case",
                    description=description or name,
                    anchor_phrases=anchors,
                )
            )

    policies: list[PolicyDraft] = []
    for item in policies_raw:
        if not isinstance(item, dict):
            continue
        statement = str(item.get("statement", "")).strip()
        policy_type = _normalize_policy_type(item.get("type"))
        anchors = _normalize_anchors(statement, item.get("anchor_phrases"))
        if statement:
            policies.append(
                PolicyDraft(
                    statement=statement,
                    type=policy_type,
                    anchor_phrases=anchors,
                )
            )

    return use_cases, policies


def _find_anchor_line(doc: MarkdownDocument, anchors: list[str]) -> int | None:
    lowered_anchors = [a.lower() for a in anchors if a.strip()]
    for idx, line in enumerate(doc.lines, start=1):
        lowered_line = line.lower()
        if any(anchor in lowered_line for anchor in lowered_anchors):
            return idx
    return None


def _evidence_from_anchors(doc: MarkdownDocument, anchors: list[str]) -> list[Evidence]:
    line_idx = _find_anchor_line(doc, anchors)
    if line_idx is None:
        return []
    quote = doc.quote(line_idx, line_idx)
    return [
        Evidence(
            input_file=Path(doc.path).name,
            line_start=line_idx,
            line_end=line_idx,
            quote=quote,
        )
    ]


def extract_use_cases_drafts(
    doc: MarkdownDocument,
    drafts: list[UseCaseDraft],
) -> list[UseCase]:
    factory = IdFactory("uc_")
    results: list[UseCase] = []
    for draft in drafts:
        evidence = _evidence_from_anchors(doc, draft.anchor_phrases)
        if not evidence:
            continue
        results.append(
            UseCase(
                id=factory.new(draft.name),
                case="",
                name=sanitize_markdown_text(draft.name),
                description=sanitize_markdown_text(draft.description),
                evidence=evidence,
            )
        )
    return results


def extract_policies_drafts(
    doc: MarkdownDocument,
    drafts: list[PolicyDraft],
) -> list[Policy]:
    factory = IdFactory("pol_")
    results: list[Policy] = []
    for draft in drafts:
        evidence = _evidence_from_anchors(doc, draft.anchor_phrases)
        if not evidence:
            continue
        results.append(
            Policy(
                id=factory.new(draft.statement),
                case="",
                type=_normalize_policy_type(draft.type),
                statement=sanitize_markdown_text(draft.statement),
                evidence=evidence,
            )
        )
    return results

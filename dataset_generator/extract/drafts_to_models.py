from __future__ import annotations

from pathlib import Path

from dataset_generator.core.ids import IdFactory
from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.core.models import Evidence, Policy, UseCase
from dataset_generator.core.text_sanitize import sanitize_markdown_text
from dataset_generator.extract.drafts import PolicyDraft, UseCaseDraft

_ALLOWED_POLICY_TYPES = {"must", "must_not", "escalate", "style", "format"}


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


def drafts_to_use_cases(
    drafts: list[UseCaseDraft],
    doc: MarkdownDocument,
    case: str,
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
                case=case,
                name=sanitize_markdown_text(draft.name),
                description=sanitize_markdown_text(draft.description),
                evidence=evidence,
            )
        )
    return results


def drafts_to_policies(
    drafts: list[PolicyDraft],
    doc: MarkdownDocument,
    case: str,
) -> list[Policy]:
    factory = IdFactory("pol_")
    results: list[Policy] = []
    for draft in drafts:
        evidence = _evidence_from_anchors(doc, draft.anchor_phrases)
        if not evidence:
            continue
        policy_type = draft.type if draft.type in _ALLOWED_POLICY_TYPES else "must"
        results.append(
            Policy(
                id=factory.new(draft.statement),
                case=case,
                type=policy_type,
                statement=sanitize_markdown_text(draft.statement),
                evidence=evidence,
            )
        )
    return results

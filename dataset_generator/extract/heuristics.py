from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from dataset_generator.core.ids import IdFactory
from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.core.models import Evidence, Policy, UseCase
from dataset_generator.core.text_sanitize import sanitize_markdown_text


_FAQ_PREFIXES = ("q:", "q.", "вопрос:")
_LIST_PREFIXES = ("- ", "* ")

_POLICY_KEYWORDS = [
    "нельзя",
    "должен",
    "должна",
    "должны",
    "запрещено",
    "эскалация",
    "конфиденциальность",
]

_POLICY_TYPE_MAP = [
    ("нельзя", "must_not"),
    ("запрещ", "must_not"),
    ("эскалац", "escalate"),
    ("вежлив", "style"),
    ("формат", "format"),
]


def _policy_type_for_text(text: str) -> str:
    lowered = text.lower()
    for key, ptype in _POLICY_TYPE_MAP:
        if key in lowered:
            return ptype
    return "must"


@dataclass(frozen=True)
class _Section:
    start: int
    end: int
    title: str


def _is_header(line: str) -> bool:
    return line.lstrip().startswith("#")


def _header_title(line: str) -> str:
    return line.lstrip("#").strip()


def _collect_sections(lines: list[str]) -> list[_Section]:
    sections: list[_Section] = []
    current_start: int | None = None
    current_title = ""
    for idx, line in enumerate(lines, start=1):
        if _is_header(line):
            if current_start is not None:
                sections.append(_Section(current_start, idx - 1, current_title))
            current_start = idx
            current_title = _header_title(line) or "Section"
    if current_start is not None:
        sections.append(_Section(current_start, len(lines), current_title))
    return sections


def _collect_list_items(lines: list[str]) -> list[_Section]:
    items: list[_Section] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(_LIST_PREFIXES):
            title = stripped.lstrip("-* ").strip() or "Item"
            items.append(_Section(idx, idx, title))
    return items


def _collect_faq(lines: list[str]) -> list[_Section]:
    items: list[_Section] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip().lower()
        if any(stripped.startswith(prefix) for prefix in _FAQ_PREFIXES):
            end = idx
            if idx < len(lines) and lines[idx].strip().lower().startswith("a:"):
                end = idx + 1
            title = lines[idx - 1].strip() or "FAQ"
            items.append(_Section(idx, end, title))
    return items


def _dedupe_sections(sections: Iterable[_Section]) -> list[_Section]:
    result: list[_Section] = []
    used: set[tuple[int, int]] = set()
    for sec in sections:
        key = (sec.start, sec.end)
        if key in used:
            continue
        used.add(key)
        result.append(sec)
    return result


def extract_use_cases(doc: MarkdownDocument, n: int) -> list[UseCase]:
    sections = []
    sections.extend(_collect_sections(doc.lines))
    sections.extend(_collect_list_items(doc.lines))
    sections.extend(_collect_faq(doc.lines))
    sections = _dedupe_sections(sections)

    factory = IdFactory("uc_")
    use_cases: list[UseCase] = []
    for sec in sections:
        if len(use_cases) >= n:
            break
        quote = doc.quote(sec.start, sec.end)
        evidence = [
            Evidence(
                input_file=Path(doc.path).name,
                line_start=sec.start,
                line_end=sec.end,
                quote=quote,
            )
        ]
        name = sanitize_markdown_text(sec.title)
        description = sanitize_markdown_text(quote)
        use_cases.append(
            UseCase(
                id=factory.new(sec.title),
                case="",
                name=name,
                description=description,
                evidence=evidence,
            )
        )
    return use_cases


def extract_policies(doc: MarkdownDocument, n: int) -> list[Policy]:
    factory = IdFactory("pol_")
    policies: list[Policy] = []
    for idx, line in enumerate(doc.lines, start=1):
        lowered = line.lower()
        if any(keyword in lowered for keyword in _POLICY_KEYWORDS):
            if len(policies) >= n:
                break
            quote = doc.quote(idx, idx)
            evidence = [
                Evidence(
                    input_file=Path(doc.path).name,
                    line_start=idx,
                    line_end=idx,
                    quote=quote,
                )
            ]
            statement = sanitize_markdown_text(line.strip())
            policy_type = _policy_type_for_text(statement)
            policies.append(
                Policy(
                    id=factory.new(line.strip()),
                    case="",
                    type=policy_type,
                    statement=statement,
                    evidence=evidence,
                )
            )
    return policies

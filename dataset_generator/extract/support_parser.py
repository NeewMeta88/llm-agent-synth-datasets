from __future__ import annotations

import re

from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.core.text_sanitize import sanitize_markdown_text


_FAQ_HEADER_RE = re.compile(r"^\s*##\s+.*FAQ", re.IGNORECASE)
_TICKETS_HEADER_RE = re.compile(r"^\s*##\s+.*выгрузк", re.IGNORECASE)
_TABLE_ROW_RE = re.compile(r"^\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")


def parse_support_faq(doc: MarkdownDocument) -> list[str]:
    items: list[str] = []
    in_faq = False
    for line in doc.lines:
        if line.lstrip().startswith("# "):
            in_faq = False
        if _FAQ_HEADER_RE.search(line):
            in_faq = True
            continue
        if in_faq:
            if line.lstrip().startswith("#"):
                in_faq = False
                continue
            if re.match(r"^\s*\d+\.", line):
                text = sanitize_markdown_text(line)
                if ":" in text:
                    text = text.split(":", 1)[0].strip()
                if text:
                    items.append(text)
    return items


def parse_support_tickets(doc: MarkdownDocument) -> list[dict]:
    rows: list[dict] = []
    in_table = False
    for line in doc.lines:
        if _TICKETS_HEADER_RE.search(line):
            in_table = True
            continue
        if line.lstrip().startswith("# "):
            in_table = False
        if not in_table:
            continue
        match = _TABLE_ROW_RE.match(line)
        if not match:
            continue
        if "---" in line:
            continue
        ticket_id = match.group(1).strip()
        user_message = match.group(2).strip()
        operator_answer = match.group(3).strip()
        if not ticket_id.isdigit():
            continue
        user_message = sanitize_markdown_text(user_message.strip("«»\""))
        operator_answer = sanitize_markdown_text(operator_answer.strip("«»\""))
        rows.append(
            {
                "ticket_id": ticket_id,
                "user_message": user_message,
                "operator_answer": operator_answer,
            }
        )
    return rows

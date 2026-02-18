from __future__ import annotations

import re


_LIST_MARKER_RE = re.compile(r"^\s*(\d+\.\s+|[\*\-]\s+)")
_HEADER_RE = re.compile(r"^\s*#+\s+")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def sanitize_markdown_text(text: str) -> str:
    if not text:
        return ""

    cleaned = text.replace("\\+", "+").replace("\\_", "_")
    cleaned = _HEADER_RE.sub("", cleaned)
    cleaned = _LIST_MARKER_RE.sub("", cleaned)
    cleaned = _BOLD_RE.sub(r"\1", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"[ \t]+$", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()

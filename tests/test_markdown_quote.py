from pathlib import Path

import pytest

from dataset_generator.core.markdown import MarkdownDocument


def test_quote_exact_match(tmp_path: Path) -> None:
    content = """# Title
Line one
Line two

Line four
"""
    file_path = tmp_path / "doc.md"
    file_path.write_text(content, encoding="utf-8")

    doc = MarkdownDocument.read(str(file_path))
    assert doc.quote(2, 4) == "Line one\nLine two\n"


@pytest.mark.parametrize(
    "start,end",
    [
        (0, 1),
        (1, 0),
        (3, 2),
        (1, 100),
        (-1, 1),
    ],
)
def test_quote_invalid_ranges(start: int, end: int, tmp_path: Path) -> None:
    file_path = tmp_path / "doc.md"
    file_path.write_text("a\nb\nc\n", encoding="utf-8")
    doc = MarkdownDocument.read(str(file_path))

    with pytest.raises(ValueError):
        doc.quote(start, end)

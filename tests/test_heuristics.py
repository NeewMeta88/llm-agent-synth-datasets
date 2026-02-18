from pathlib import Path

from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.extract.heuristics import extract_policies, extract_use_cases


def test_heuristics_extract(tmp_path: Path) -> None:
    content = """# Заголовок
Описание раздела.

- Пункт списка один
- Пункт списка два

FAQ
Q: Как восстановить пароль?
A: Нажмите кнопку.

Оператор должен уточнить детали.
Запрещено передавать данные третьим лицам.
"""
    file_path = tmp_path / "doc.md"
    file_path.write_text(content, encoding="utf-8")

    doc = MarkdownDocument.read(str(file_path))
    use_cases = extract_use_cases(doc, n=5)
    policies = extract_policies(doc, n=5)

    assert len(use_cases) >= 2
    assert len(policies) >= 2

    for uc in use_cases:
        for ev in uc.evidence:
            assert ev.quote
            assert ev.quote == doc.quote(ev.line_start, ev.line_end)

    for pol in policies:
        for ev in pol.evidence:
            assert ev.quote
            assert ev.quote == doc.quote(ev.line_start, ev.line_end)

from pathlib import Path

from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.extract.support_parser import parse_support_faq, parse_support_tickets


def test_support_parser_extracts_items() -> None:
    path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    doc = MarkdownDocument.from_file(str(path))

    tickets = parse_support_tickets(doc)
    faq = parse_support_faq(doc)

    assert len(tickets) >= 10
    assert len(faq) >= 5

    for ticket in tickets:
        user_message = ticket.get("user_message", "")
        assert "|" not in user_message
        assert "**" not in user_message
        assert "\\+" not in user_message

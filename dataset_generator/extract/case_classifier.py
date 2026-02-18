from __future__ import annotations

from typing import Literal

CaseType = Literal["support_bot", "operator_quality", "auto"]


_SUPPORT_KEYWORDS = [
    "faq",
    "клиент",
    "оператор",
    "тикет",
    "tickets",
    "вопрос",
    "ответ",
    "поддержк",
]

_OPERATOR_QUALITY_KEYWORDS = [
    "исправь",
    "качество",
    "проверки",
    "валидац",
    "диалог",
    "оператор",
    "ответ оператора",
]


def detect_case(lines: list[str], case_override: CaseType = "auto") -> Literal[
    "support_bot", "operator_quality"
]:
    if case_override != "auto":
        return case_override

    text = "\n".join(lines).lower()

    score_support = sum(1 for kw in _SUPPORT_KEYWORDS if kw in text)
    score_operator = sum(1 for kw in _OPERATOR_QUALITY_KEYWORDS if kw in text)

    if score_operator >= score_support and score_operator > 0:
        return "operator_quality"
    return "support_bot"

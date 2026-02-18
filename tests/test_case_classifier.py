from dataset_generator.extract.case_classifier import detect_case


def test_detect_case_support_bot() -> None:
    lines = [
        "FAQ",
        "Клиент: Как восстановить пароль?",
        "Оператор: Используйте ссылку сброса.",
    ]
    assert detect_case(lines) == "support_bot"


def test_detect_case_operator_quality() -> None:
    lines = [
        "Правила проверки качества оператора",
        "Исправь грамматику и орфографию.",
        "Диалог:",
    ]
    assert detect_case(lines) == "operator_quality"

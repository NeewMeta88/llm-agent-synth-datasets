from pathlib import Path

from tools.extract_examples_from_tz import main


def test_examples_synced_with_tz(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tz_path = repo_root / (
        "ТЗ. Постановка задачи. Генерация синтетических датасетов для тестирования LLM-агентов.md"
    )
    out_dir = tmp_path / "examples"

    monkeypatch.chdir(repo_root)
    main(["--tz", str(tz_path), "--out-dir", str(out_dir)])

    support_path = out_dir / "example_input_raw_support_faq_and_tickets.md"
    operator_checks_path = out_dir / "example_input_raw_operator_quality_checks.md"
    operator_path = out_dir / "example_input_raw_operator_quality.md"

    assert support_path.exists()
    assert operator_checks_path.exists()
    assert operator_path.exists()

    support_text = support_path.read_text(encoding="utf-8")
    assert "FAQ" in support_text
    assert "Выгрузка обращений" in support_text
    assert "ticket_id" in support_text

    operator_text = operator_checks_path.read_text(encoding="utf-8")
    assert "контекстных" in operator_text
    assert "бесконтекстных" in operator_text
    assert "Пример диалога" in operator_text

    doctor_path = out_dir / "example_input_raw_doctor_booking.md"
    if doctor_path.exists():
        doctor_text = doctor_path.read_text(encoding="utf-8")
        assert "Здоровье+" in doctor_text

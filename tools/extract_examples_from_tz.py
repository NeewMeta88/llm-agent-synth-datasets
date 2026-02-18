from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_TZ_PATH = (
    "ТЗ. Постановка задачи. Генерация синтетических датасетов для тестирования LLM-агентов.md"
)

HEADINGS = {
    "# example_input_raw_operator_quality_checks.md": "example_input_raw_operator_quality_checks.md",
    "# example_input_raw_support_faq_and_tickets.md": "example_input_raw_support_faq_and_tickets.md",
    "# example_input_raw_doctor_booking": "example_input_raw_doctor_booking.md",
}


def normalize_heading(text: str) -> str:
    return text.replace("\\_", "_").strip()


def _extract_sections(lines: list[str]) -> dict[str, list[str]]:
    normalized_targets = {normalize_heading(k): k for k in HEADINGS}
    sections: dict[str, list[str]] = {}

    current_key: str | None = None
    current_lines: list[str] = []

    def _commit() -> None:
        nonlocal current_key, current_lines
        if current_key is None:
            return
        sections[current_key] = current_lines
        current_key = None
        current_lines = []

    for line in lines:
        if line.startswith("# "):
            normalized = normalize_heading(line.strip())
            if normalized in normalized_targets:
                _commit()
                current_key = normalized_targets[normalized]
                current_lines = []
                continue
        if current_key is not None:
            current_lines.append(line)

    _commit()
    return sections


def _read_text_guessing(path: Path) -> str:
    raw = path.read_bytes()
    utf8_text = raw.decode("utf-8", errors="ignore")
    for encoding in ("utf-8", "cp1251"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        if any("А" <= ch <= "я" for ch in text):
            return text
    return utf8_text


def _write_section(out_dir: Path, filename: str, lines: list[str]) -> Path:
    out_path = out_dir / filename
    content = "\n".join(lines).replace("\\_", "_").strip() + "\n"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract example inputs from TZ.")
    parser.add_argument("--tz", default=DEFAULT_TZ_PATH, help="Path to TZ markdown file.")
    parser.add_argument("--out-dir", default="examples", help="Output directory.")
    args = parser.parse_args(argv)

    tz_path = Path(args.tz)
    if not tz_path.exists():
        raise SystemExit(f"TZ file not found: {tz_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = _read_text_guessing(tz_path).splitlines()
    sections = _extract_sections(lines)

    for heading, filename in HEADINGS.items():
        normalized = normalize_heading(heading)
        if normalized not in sections:
            continue
        _write_section(out_dir, filename, sections[normalized])

    support_main = out_dir / "example_input_raw_support_faq_and_tickets.md"
    operator_main = out_dir / "example_input_raw_operator_quality_checks.md"

    if support_main.exists():
        (out_dir / "example_input_raw_support.md").write_text(
            support_main.read_text(encoding="utf-8"), encoding="utf-8"
        )
    if operator_main.exists():
        (out_dir / "example_input_raw_operator_quality.md").write_text(
            operator_main.read_text(encoding="utf-8"), encoding="utf-8"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

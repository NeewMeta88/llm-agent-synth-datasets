from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MarkdownDocument:
    path: str
    lines: list[str]

    @property
    def n_lines(self) -> int:
        return len(self.lines)

    @classmethod
    def read(cls, path: str) -> "MarkdownDocument":
        raw = Path(path).read_bytes()
        for encoding in ("utf-8", "cp1251"):
            try:
                text = raw.decode(encoding)
            except UnicodeDecodeError:
                continue
            if any("А" <= ch <= "я" for ch in text):
                return cls(path=path, lines=text.splitlines())
        return cls(path=path, lines=raw.decode("utf-8", errors="ignore").splitlines())

    @classmethod
    def from_file(cls, path: str) -> "MarkdownDocument":
        return cls.read(path)

    def quote(self, line_start: int, line_end: int) -> str:
        if line_start < 1 or line_end < 1 or line_start > line_end:
            raise ValueError("Invalid line range")
        if line_end > self.n_lines:
            raise ValueError("Invalid line range")
        return "\n".join(self.lines[line_start - 1 : line_end])

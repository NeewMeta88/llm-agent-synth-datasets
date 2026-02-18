from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

_ALLOWED_PREFIXES = {"uc_", "pol_", "tc_", "ex_"}


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    spaced = re.sub(r"\s+", "-", lowered)
    cleaned = re.sub(r"[^a-z0-9-]", "", spaced)
    collapsed = re.sub(r"-+", "-", cleaned)
    return collapsed.strip("-")


@dataclass
class IdFactory:
    prefix: str
    _seen: set[str] = field(default_factory=set, init=False, repr=False)
    _counts: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.prefix not in _ALLOWED_PREFIXES:
            raise ValueError("Unsupported prefix")

    def new(self, text_seed: str) -> str:
        base = f"{self.prefix}{slugify(text_seed)}"
        if base not in self._seen:
            self._seen.add(base)
            self._counts[base] = 1
            return base

        count = self._counts.get(base, 1) + 1
        self._counts[base] = count
        candidate = f"{base}_{count}"
        while candidate in self._seen:
            count += 1
            self._counts[base] = count
            candidate = f"{base}_{count}"
        self._seen.add(candidate)
        return candidate

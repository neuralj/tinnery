"""Small local JSONL evidence journal (single-writer, not tamper-proof)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .contract import canonical_json


class EvidenceJournal:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append_execution(self, receipt: Any) -> None:
        self._append("execution_receipt", receipt.to_dict())

    def append_verification(self, record: Any) -> None:
        self._append("verification_record", record.to_dict())

    def _append(self, record_type: str, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = canonical_json({"journal_version": "1", "record_type": record_type, "record": record}) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

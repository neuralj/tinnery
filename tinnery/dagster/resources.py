"""Dagster Resource holding an optional EvidenceJournal.

持有可选 EvidenceJournal 的 Dagster Resource。
"""

from pathlib import Path

from tinnery.evidence import EvidenceJournal


class TinneryResource:
    """Dagster resource that optionally persists execution receipts.

    可选持久化执行回执的 Dagster resource。

    Passed to Dagster as a plain Python object (Dagster wraps it as a
    hardcoded resource at execution time).

    作为普通 Python 对象传入 Dagster（Dagster 在执行时将其包装为硬编码资源）。
    """

    def __init__(self, journal_path: str | Path | None = None):
        self._journal = EvidenceJournal(journal_path) if journal_path else None

    @property
    def journal(self) -> EvidenceJournal | None:
        return self._journal

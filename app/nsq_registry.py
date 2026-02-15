from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NSQRegistry:
    """Loads known CDSCO NSQ records for exact batch/manufacturer matching."""

    def __init__(self, dataset_path: str = "data/cdsco_nsq_dec25_subset.json") -> None:
        self.dataset_path = Path(dataset_path)
        self._records: list[dict[str, Any]] = []
        if self.dataset_path.exists():
            self._records = json.loads(self.dataset_path.read_text(encoding="utf-8"))

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(value.lower().strip().split())

    def find_exact_match(self, batch_number: str, manufacturer: str) -> dict[str, Any] | None:
        b = self._norm(batch_number)
        m = self._norm(manufacturer)
        for row in self._records:
            if self._norm(row.get("batch_number", "")) == b and m in self._norm(row.get("manufacturer", "")):
                return row
        return None

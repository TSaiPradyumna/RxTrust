#!/usr/bin/env python3
"""Run the user-provided NSQ sample cases without external dependencies."""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path("data/cdsco_nsq_dec25_subset.json")


def norm(s: str) -> str:
    return " ".join(s.lower().split())


def verdict_for_issue(issue: str) -> str:
    issue_l = issue.lower()
    if "microbial" in issue_l or "impur" in issue_l:
        return "🔴 ALERT"
    if "assay" in issue_l or "dissolution" in issue_l or "related" in issue_l:
        return "🔴 ALERT"
    return "🟡 CAUTION"


def main() -> None:
    rows = json.loads(DATA.read_text(encoding="utf-8"))

    print("id | product | batch | manufacturer | verdict | reason")
    print("-" * 140)
    for row in rows:
        verdict = verdict_for_issue(row["issue"])
        print(
            f"{row['id']} | {row['product']} | {row['batch_number']} | {row['manufacturer']} | {verdict} | {row['issue']}"
        )

    # user asked if this will work on personal PC
    print("\nStatus: ✅ This script runs on a personal PC with Python 3.9+ (no pip dependencies).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Merge data/parts/*.json (each a JSON array of research records) into one file.

  python scripts/merge_parts.py <output.json>

Validates that the merged set has exactly 100 records with unique, contiguous ids.
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "research_full.json")
    records: list[dict] = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "parts", "*.json"))):
        records.extend(json.load(open(path)))
    records.sort(key=lambda r: r["id"])
    ids = [r["id"] for r in records]
    assert len(records) == 100, f"expected 100, got {len(records)}"
    assert ids == list(range(1, 101)), "ids not 1..100 contiguous/unique"
    json.dump(records, open(out, "w"), indent=2)
    print(f"[merge] {len(records)} records -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

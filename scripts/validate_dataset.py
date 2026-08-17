#!/usr/bin/env python3
"""
Validate the final dataset against the schema and re-derive buildability from the
deterministic scorer. Fails loudly if any record is invalid or if a stored
buildability label/score disagrees with the rubric. This is the QA gate.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.schema import validate_record  # noqa: E402
from pipeline.scoring.buildability import score_record  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    dataset = json.load(open(os.path.join(ROOT, "data", "final", "dataset.json")))
    problems = 0

    if len(dataset) != 100:
        print(f"FAIL: expected 100 apps, got {len(dataset)}")
        problems += 1

    apps = [r["app"] for r in dataset]
    if len(set(apps)) != len(apps):
        print("FAIL: duplicate apps present")
        problems += 1

    cats = {r["category"] for r in dataset}
    if len(cats) != 10:
        print(f"FAIL: expected 10 categories, got {len(cats)}")
        problems += 1

    for r in dataset:
        errs = validate_record(r)
        if errs:
            problems += 1
            print(f"INVALID {r['id']:>3} {r['app']}: {errs}")
        score, label, _ = score_record(r)
        if score != r.get("buildability_score") or label != r.get("buildability"):
            problems += 1
            print(f"RUBRIC MISMATCH {r['app']}: stored=({r.get('buildability_score')},{r.get('buildability')}) "
                  f"computed=({score},{label})")

    if problems == 0:
        print(f"OK: {len(dataset)} apps valid, {len(cats)} categories, scores match rubric.")
        return 0
    print(f"\n{problems} problem(s) found.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
